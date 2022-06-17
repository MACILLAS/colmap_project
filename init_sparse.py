import argparse
import pandas as pd
import numpy as np
import os
import json
from database import COLMAPDatabase

def parse_args ():
    parser = argparse.ArgumentParser(description="Create sparse models and init colmap database")

    parser.add_argument(
        '--data_dir', type=str, required=True,
        help="Folder containing extracted ROS bags."
    )

    parser.add_argument(
        '--defect_dir', type=str, required=True,
        help="defect_dir in data_dir of the scene (extracted bag of a scene)"
    )

    parser.add_argument(
        '--img_dir', type=str, required=True,
        help="Directory where images are stored in the defect_dir"
    )

    parser.add_argument(
        '--output_dir', type=str, required=True,
        help="Where the database and sparse model should be stored"
    )

    args = parser.parse_args()

    data_dir = args.data_dir
    defect_dir = args.defect_dir
    img_dir = args.img_dir
    output_dir = args.output_dir

    if not os.path.exists(data_dir):
        raise NotADirectoryError
        exit()

    if not os.path.exists(os.path.join(data_dir, defect_dir)):
        raise NotADirectoryError
        exit()

    if not os.path.exists(os.path.join(data_dir, defect_dir, img_dir)):
        raise NotADirectoryError
        exit()

    return data_dir, defect_dir, img_dir, output_dir

def get_pose (image_name="1", poses=None):
    """
    Assume the images are in the format 1.jpg, 2.jpg etc. What is passed is 1, 2, etc.
    Assume pose dataframe column 0 is [1...num_img] columns [1..7] are qw, qx, qy, qz, tx, ty
    :param image_name: number of the image should match that of poses df
    :param poses: pose dataframe
    :return: qw, qx, qy, qz, tx, ty
    """
    row = poses.loc[poses.iloc[:, 0] == int(image_name)]
    qw, qx, qy, qz, tx, ty, tz = row.iloc[0, 1:]
    return qw, qx, qy, qz, tx, ty, tz

def build_colmap_db (data_dir, defect_dir, img_dir, output_dir):
    """
    Initialize colmap database that will be used to create a sparse sfm model
    ** assumes there is only one camera model for each scene (this is a valid assumption since CVISS will collect data
    with our propriety hardware **
    :param data_dir: Directory to our data
    :param defect_dir: Directory in data_dir of the scene (extracted bag of a scene)
    :param img_dir: Where the images are stored in the defect_dir
    :param output_dir: Directory where the created db is saved (output_dir/<defect_dir>_colmap.db)
    """

    images_dir = os.listdir((os.path.join(data_dir, defect_dir, img_dir)))
    poses = pd.read_csv(os.path.join(data_dir, defect_dir, 'poses.csv'), header=None)

    # Assume same camera (only 1 camera)
    with open(os.path.join(data_dir, defect_dir, 'intrinsics.json'), 'r') as f:
        camera_intrinsics = json.load(f)

    # camera matrix is the intrinsic parameters matrix (3x3)
    # The structure of which is [fx, 0, px]; [0, fy, py]; [0, 0, 1]
    # Colmap Pinhole camera models has the parameters list (fx, fy, cx, cy)
    # MODEL: 0 "SIMPLE_PINHOLE" 3
    # MODEL: 1 "PINHOLE" 4
    fx = camera_intrinsics["camera_matrix"][0][0]
    fy = camera_intrinsics["camera_matrix"][1][1]
    cx = camera_intrinsics["camera_matrix"][0][2]
    cy = camera_intrinsics["camera_matrix"][1][2]
    model1, width1, height1, params1 = 1, camera_intrinsics['width'], camera_intrinsics['height'], np.array((fx, fy, cx, cy))

    # Initialize ColmapDatabase
    print(os.path.join(output_dir, str(defect_dir + "_colmap.db")))
    db = COLMAPDatabase.connect(os.path.join(output_dir, str(defect_dir + "_colmap.db")))

    # For convenience, try creating all the tables upfront.
    db.create_tables()

    camera_id1 = db.add_camera(model1, width1, height1, params1)

    # Initialize cameras.txt, images.txt and points3D.txt
    # According to FAQs
    # points3D.txt should be empty
    # images.txt every other line should be empty
    # cameras.txt can use same format (camera_intrinsics)

    # Create blank images.txt and points3D.txt
    open(os.path.join(output_dir, 'points3D.txt'), 'w')
    f = open(os.path.join(output_dir, 'images.txt'), 'w')

    # create cameras.txt
    c = open(os.path.join(output_dir, 'cameras.txt'), 'w')
    c.write("# Camera list with one line of data per camera:\n")
    c.write("# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
    c.write("# Number of cameras: 1\n")
    c.write("1 " + "PINHOLE " + str(width1) + " " + str(height1) + " " + str(params1)[1:-1])
    c.close()

    counter = 1
    images_dir.sort()
    for image in images_dir:

        img_idx = image[:-4]
        print(str(img_idx))

        # Write cameras.txt, images.txt, points3D.txt
        qw, qx, qy, qz, tx, ty, tz = get_pose(img_idx, poses)
        qt_ts_str = str(qw) + " " + str(qx) + " " + str(qy) + " " + str(qz) + " " + str(tx) + " " + str(ty) + " " + str(tz)
        f.write(str(counter) + " " + qt_ts_str + " " + str(1) + " " + image+"\n\n")
        counter = counter + 1
        image_ids = db.add_image(image, camera_id1, np.array((qw, qx, qy, qz)), np.array((tx, ty, tz)))

    # Commit the data to the file.
    db.commit()
    db.close()
    f.close()

# MAIN Routine
#build_colmap_db(data_dir, defect_dir, img_dir, output_dir)

if __name__ == "__main__":
    ## DEBUG ##
    data_dir, defect_dir, img_dir, output_dir = parse_args()
    #data_dir = '/media/cviss3/Expansion/Data/HL2/21-06-06 gardiner/images+poses'
    #defect_dir = 'defect_1b'
    #img_dir = 'images'
    #output_dir = os.path.join(data_dir, defect_dir)

    build_colmap_db(data_dir, defect_dir, img_dir, output_dir)