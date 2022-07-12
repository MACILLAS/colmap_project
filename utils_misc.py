import h5py
import os
import numpy as np
import pandas as pd
import read_write_dense
import pre_process_depth
import cv2
import natsort
import shutil


def sample_images(imgdir, csvdir, keepfreq):
    img_dirs = os.listdir(imgdir)
    pose_df = pd.read_csv(csvdir, header=None)
    img_out_dir = os.path.join(imgdir, 'rgb_samp')
    os.mkdir(img_out_dir)
    imgdirs = natsort.natsorted(img_dirs)

    counter = 0
    for img in imgdirs:
        counter = counter + 1
        if counter % keepfreq == 0:
            shutil.copyfile(os.path.join(imgdir, img), os.path.join(img_out_dir, img))
        else:
            pose_df = pose_df.drop(pose_df[pose_df[0] == counter].index)

    pose_df.to_csv(os.path.join(img_out_dir, "poses.csv"), header=None, index=False)

def mv_bin_n_h5(binary_dir=None, output_h5_dir=None, max_range=3.5, convert_mm_to_m=False):
    '''
    This function takes the directory of the binary depth map.
    :param binary_dir:
    :param output_h5_dir:
    :return:
    '''
    depth_dirs = os.listdir(binary_dir)

    for depth_bin in depth_dirs:
        if depth_bin.split('.')[2] == "photometric":
            pass
        depth_name = depth_bin.split('.')[0]
        depth_map = read_write_dense.read_array(os.path.join(binary_dir, depth_bin))

        min_depth, max_depth = np.percentile(depth_map, [5, 95])
        depth_map[depth_map < min_depth] = min_depth
        depth_map[depth_map > max_depth] = max_depth

        # depth_map = pre_process_depth.filter_depth(depth_map, max_range, convert_mm_to_m)

        pre_process_depth.save_depth_as_h5(depth_map, output_h5_dir, depth_name)


def create_pose_csv(in_dir, out_dir):
    pose_texts = os.listdir(in_dir)

    for ii in range(len(pose_texts)):
        pose = np.loadtxt(os.path.join(in_dir, 'pose_%i.txt' % ii))

    raise NotImplementedError


def resize_imgs(indir, new_size):
    imgs = os.listdir(indir)

    for img_name in imgs:
        img = cv2.imread(os.path.join(indir, img_name), -1)
        img = cv2.resize(img, new_size)
        cv2.imwrite(os.path.join(indir, img_name), img)


if __name__ == "__main__":
    # mv_bin_n_h5(binary_dir=str("/media/cviss3/Expansion/Data/HL2/21-06-06 gardiner/images+poses/defect_1a/dense/stereo/depth_maps"), output_h5_dir=str("/media/cviss3/Expansion/LoFTR_our_data/dummy_struct/phoenix/S6/zl548/MegaDepth_v1/defect_1a/dense0/depths"))
    # create_pose_csv()
    # resize_imgs("/media/cviss3/Expansion/LoFTR_our_data/dummy_struct/Undistorted_SfM/defect_3/images", (2000, 1125))
    csv_dir = '/media/cviss3/Expansion/Data/22-06-28-ParkingGarage-processed/robot_2022-06-28-13-17-46/'
    sample_images(os.path.join(csv_dir, 'rgb'), os.path.join(csv_dir, 'poses.csv'), 5)
