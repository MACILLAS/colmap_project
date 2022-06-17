import h5py
import os
import numpy as np
import read_write_dense
import pre_process_depth

def mv_bin_n_h5 (binary_dir=None, output_h5_dir=None, max_range=3.5, convert_mm_to_m=False):
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

        #depth_map = pre_process_depth.filter_depth(depth_map, max_range, convert_mm_to_m)

        pre_process_depth.save_depth_as_h5(depth_map, output_h5_dir, depth_name)

#if __name__ == "__main__":
    #mv_bin_n_h5(binary_dir=str("/media/cviss3/Expansion/Data/HL2/21-06-06 gardiner/images+poses/defect_1a/dense/stereo/depth_maps"), output_h5_dir=str("/media/cviss3/Expansion/LoFTR_our_data/dummy_struct/phoenix/S6/zl548/MegaDepth_v1/defect_1a/dense0/depths"))
