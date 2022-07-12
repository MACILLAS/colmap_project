import h5py
import os
import cv2
import argparse

"""
This function takes data_path and output_path as inputs...
Assume data_path contains depth and rgb sub-folders.  
For each file in rgb read the corresponding depth image;
process it and save it in compatible h5 format in the output_path.=-    
Reading saved h5 using the following code snipit
hdf5_file_read = h5py.File(os.path.join(depth_path, str(img_name+".h5")), 'r')
gt = hdf5_file_read.get('/depth')
gt = np.array(gt)
"""


def parse_args():
    parser = argparse.ArgumentParser(description='Pre-Processing Our Depth Script. Sample Usage: \
    python pre_process_depth.py --data_path /media/cviss3/Expansion/21-06-06\ gardiner\ intel\ realsense/images/defect_1 \
    --output_path /media/cviss3/Expansion/21-06-06\ gardiner\ intel\ realsense/colmap_project/undistorted_sparse_txt_defect_1/depth/')

    parser.add_argument(
        '--data_path', type=str, required=True,
        help='i.e., path to defect_x folder, should have depth and rgb sub-folders'
    )

    parser.add_argument(
        '--output_path', type=str, required=True,
        help='path to the output directory (i.e., where you are saving .h5 files)'
    )

    args = parser.parse_args()
    return args


def filter_depth(depth_map=None, max_range=3.5, convert_mm_to_m=False):
    """
    This function processes the inputted depth_map
    :param depth_map: depth_map ndarray
    :param max_range: the maximum range of sensor (Intel Realsense 3.5 m)
    :param convert_mm_to_m: draw data (png) maybe in mm. Divide by 1000 to get meters.
    :return: processed ndarray
    """
    raise DeprecationWarning
    if convert_mm_to_m:
        depth_map = depth_map / 1000

    in_range_mask = depth_map < max_range
    depth_map = depth_map * in_range_mask
    return depth_map


def save_depth_as_h5(depth_map=None, save_dir="./", img_name="debug"):
    """
    This function takes the depth_map array
    and saves it in the save_dir with file_name
    :param depth_map: depth_map array
    :param save_dir: save directory
    :param img_name: name of the image (minus the type) (i.e., 1, 2, 3, 4...)
    :return:
    """
    h5f = h5py.File(os.path.join(save_dir, str(img_name + ".h5")), 'w')
    h5f.create_dataset("depth", data=depth_map)
    h5f.close()


def main():
    # data_path = os.path.join("/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images/defect_1")
    # depth_path = os.path.join(data_path, "depth")
    # imgs_path = os.path.join(data_path, "rgb")
    # save_dir = os.path.join(depth_path)
    # img_name = "2"
    args = parse_args()
    data_path = args.data_path
    save_path = args.output_path

    # Remove the trailing / if need be.
    if data_path[-1] in ['/', '\\']:
        base_path = data_path[: - 1]

    depth_path = os.path.join(
        data_path, 'depth'
    )
    imgs_path = os.path.join(
        data_path, 'rgb'
    )

    if not os.path.exists(depth_path):
        exit()

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    images_dir = os.listdir(imgs_path)
    images_dir.sort()

    for img_name in images_dir:
        print(img_name)
        img_name = img_name[:-4]
        # Read Images
        depth_map = cv2.imread(os.path.join(depth_path, (img_name + ".png")), cv2.IMREAD_UNCHANGED)
        # Filter Depth Images (turn pixels > 3.5 m to 0) 0 is ignored
        # depth_map = filter_depth(depth_map=depth_map, max_range=3.5, convert_mm_to_m=True)
        # Save the Depth as H5 file format
        save_depth_as_h5(depth_map=depth_map, save_dir=save_path, img_name=img_name)


if __name__ == "__main__":
    raise DeprecationWarning
    main()
