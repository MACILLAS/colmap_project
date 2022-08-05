from localization.src.utils import project_2d_to_3d
import pandas as pd
import numpy as np
from os import path
import cv2
import json
from scipy.spatial.transform import Rotation

data_dir = "/media/cviss3/Expansion/Data/22-06-28-ParkingGarage-processed/robot_2022-06-28-13-17-46"
images_dir = path.join(data_dir, "rgb")
depths_dir = path.join(data_dir, "depth")

pose_df = pd.read_csv(path.join(data_dir, "poses.csv"), header=None, index_col=None)
with open(path.join(data_dir, "intrinsics.json"), 'r') as f:
    intrinsic = json.load(f)

K = intrinsic["camera_matrix"]
K = np.array((K[0], K[1], K[2]), dtype=float)


class Frame:
    def __init__(self, df_row, K):
        self.filename = str(int(df_row[0]))
        self.D = cv2.imread(path.join(depths_dir, self.filename + ".png"), cv2.IMREAD_UNCHANGED)
        self.tc = np.array(df_row[1:4])
        self.qc = np.array(df_row[4:])
        self.K = K
        self.pts3D = None
        self.T_m1_c1 = None
        self.rvecs = None
        self.tvecs = None
        principal_axis = []
        qvec = self.qc
        qvec = qvec / np.linalg.norm(qvec)
        w, x, y, z = qvec
        R = np.array([
            [
                1 - 2 * y * y - 2 * z * z,
                2 * x * y - 2 * z * w,
                2 * x * z + 2 * y * w
            ],
            [
                2 * x * y + 2 * z * w,
                1 - 2 * x * x - 2 * z * z,
                2 * y * z - 2 * x * w
            ],
            [
                2 * x * z - 2 * y * w,
                2 * y * z + 2 * x * w,
                1 - 2 * x * x - 2 * y * y
            ]
        ])
        principal_axis.append(R[2, :])
        t = self.tc
        # World-to-Camera pose
        current_pose = np.zeros([4, 4])
        current_pose[: 3, : 3] = R
        current_pose[: 3, 3] = t
        current_pose[3, 3] = 1
        self.tr_mat = current_pose

    def img_pts_to_3d_g(self, pts):
        x_c, y_c, z_c = project_2d_to_3d(pts.T, K, self.D, h=0)
        pts3D_c = np.array([x_c, y_c, z_c, np.ones(x_c.shape[0])])

        T_m1_c1 = np.eye(4)
        T_m1_c1[:3, :3] = Rotation.from_quat(self.qc).as_matrix()
        T_m1_c1[:3, 3] = self.tc
        self.T_m1_c1 = T_m1_c1

        pts3D = T_m1_c1.dot(pts3D_c)
        pts3D = pts3D[:3, :] / pts3D[3, :]

        self.pts3D = pts3D.T
        self.recover_rvec_tvec()
        return self.pts3D

    def recover_rvec_tvec(self):
        R = self.T_m1_c1[:3, :3]
        self.rvecs = cv2.Rodrigues(R.T)[0]

        C = self.T_m1_c1[:3, 3]
        self.tvecs = -R.T.dot(C.reshape(3, 1))


def calc_overlap(frame1, frame2):
    non_zero_pts = np.argwhere(frame1.D > 0)
    number_of_rows = non_zero_pts.shape[0]
    random_indices = np.random.choice(number_of_rows, size=int(number_of_rows / 100), replace=False)
    non_zero_pts = non_zero_pts[random_indices, :]

    frame1_pts = frame1.img_pts_to_3d_g(pts=non_zero_pts)
    _ = frame2.img_pts_to_3d_g(pts=non_zero_pts)

    frame1_pts = frame1_pts[~np.isnan(frame1_pts).any(axis=1), :]
    pts2_img = \
    cv2.projectPoints(frame1_pts, frame2.rvecs, frame2.tvecs, frame2.K, np.array([0, 0, 0, 0, 0], dtype=np.float))[
        0].reshape(-1, 2)

    row, col = frame1.D.shape

    row_lower_mask = np.ma.masked_less_equal(pts2_img[:, 0], 0).mask
    col_lower_mask = np.ma.masked_less_equal(pts2_img[:, 1], 0).mask
    row_upper_mask = np.ma.masked_greater_equal(pts2_img[:, 0], row).mask
    col_upper_mask = np.ma.masked_greater_equal(pts2_img[:, 1], col).mask

    out_bnds_mask = row_lower_mask + row_upper_mask + col_upper_mask + col_lower_mask
    total_out_bnds = np.sum(np.ma.masked_greater_equal(out_bnds_mask, 1).mask)

    total_pts = frame1_pts.shape[0]
    return (total_pts - total_out_bnds) / total_pts


frame1 = Frame(pose_df.iloc[0], K)
frame2 = Frame(pose_df.iloc[2], K)

overlap = calc_overlap(frame1, frame2)
print(overlap)
'''
pts1 = np.array([[100, 100], [200, 200], [300, 300], [865, 373]])
#pts2 = np.array([[200, 200], [300, 300], [858, 379]])

frame1_pts = frame1.img_pts_to_3d_g(pts=pts1)
frame2_pts = frame2.img_pts_to_3d_g(pts=pts)

pts2_img = cv2.projectPoints(frame1_pts, frame2.rvecs, frame2.tvecs, frame2.K, np.array([0, 0, 0, 0, 0], dtype=np.float))[0].reshape(-1, 2)
print(pts2_img)
'''

# Target NPZ Format (dict)
# image_paths: (ndarray: (*,)) 'Undistorted_SfM/dir/images/*.jpg'
# depth_paths: (ndarray: (*,)) 'phoenix/S6/zl548/MegaDepth_v1/dir/dense0/depths/*.h5
# intrinsics: (ndarray: (*, 3, 3))
# poses: (ndarray: (*, 4, 4))
# pair_infos: (ndarray: (**, 3)) [[ [0, 1], overlap, [0 0 0 0] ], ... ]
