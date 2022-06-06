# This script converts NPZ files created by preprocess_scene.py to LoFTR NPZ format
# These NPZ files are then stored in /data/megadepth/index/scene_info_0.1_0.7/
# Original Author: Mihai Dusmanu
import argparse
import numpy as np

"""
a is loftr specific npz file which is actually a dictionary {dict: 5}
'image_paths' ndarray:(3803,) (for 0000_0.1_0.3.npz) if not in overlap range None
'depth_paths' ^ same
'intrinsics' ^ same None, ndarray(3x3)
'poses' ^same None, ndarray(4x4)
'pair_infos' list:256539 each list is a tuple (ndarray:(2,), float64, ndarray:(4,)) (image_pairs, overlap_score, central_matches)
central matches are never used so idk let them be zeros or some shit
"""
# a = np.load('/media/cviss3/Expansion/LoFTR_Data/loftr_megadepth_target/train-data_megadepth_indices/scene_info_0.1_0.7/0000_0.1_0.3.npz', allow_pickle=True)
"""
b has 10 npz files {list:10}
'image_paths'
'depth_paths'
'intrinsics'
'poses'
'overlap_matrix'
'angles'
'n_points3D'
'points3D_id_to_2D'
'points3D_id_to_ndepth'
"""
# b = np.load('/media/cviss3/Expansion/LoFTR_our_data/dummy_struct/gardiner_210606.npz', allow_pickle=True)

parser = argparse.ArgumentParser(description='Convert megadepth_npz to loftr compatible format.')

parser.add_argument(
    '--input', type=str, required=True,
    help='path of npz file'
)

parser.add_argument(
    '--output', type=str, required=True,
    help='saved path of output npz file'
)

args = parser.parse_args()
input_npz = args.input
output_dir = args.output


def convert_npz(b, out_name):
    overlap_mat = np.array(b['overlap_matrix'])
    # Get indexes where overlap matrix is between 0.4 and 0.7
    mask_lower = overlap_mat >= 0.5
    mask_upper = overlap_mat <= 0.7
    mask = mask_lower * mask_upper
    suf_overlap_idx = np.argwhere(mask)

    pair_infos_tuples_lst = []
    for idx in suf_overlap_idx:
        # Go through each index and append the info to build list of tuples for pair_infos
        pair_infos_tuples_lst = pair_infos_tuples_lst + [(idx, overlap_mat[idx[0]][idx[1]], np.array([0, 0, 0, 0]))]

    # Initialize dictionary
    new_dict = {"image_paths": b['image_paths'], "depth_paths": b['depth_paths'], "intrinsics": b['intrinsics'],
                "poses": b['poses'], "pair_infos": pair_infos_tuples_lst}

    # np.savez(out_name, **new_dict)
    np.savez(out_name, image_path=b['image_paths'], depth_paths=b['depth_paths'], intrinsics=b['intrinsics'],
             poses=b['poses'], pair_infos=pair_infos_tuples_lst)


def valid_npz(npz):
    scene_info = dict(np.load(npz, allow_pickle=True))
    pair_infos = scene_info['pair_infos'].copy()
    del scene_info['pair_infos']
    print("STOP")


input_npz = np.load(input_npz, allow_pickle=True)

convert_npz(input_npz, output_dir)