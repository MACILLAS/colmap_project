import subprocess
import os
import shutil
import utils_misc

_data_dir = "/media/cviss3/Expansion/Data/22-06-28-ParkingGarage-processed"
_defect_dir = "robot_2022-06-28-13-17-46"
_img_dir = "rgb"
get_depth_stereo = True
_dense_dir = os.path.join(_data_dir, _defect_dir, "dense")

"""
Simulated Loftr Data Directory Structure
"""
_dummy_base_dir = "/media/cviss3/Expansion/LoFTR_our_data/dummy_struct"
_dummy_depth_dir = os.path.join(_dummy_base_dir, "phoenix/S6/zl548/MegaDepth_v1", _defect_dir, "dense0/depths/")
_dummy_images_dir = os.path.join(_dummy_base_dir, "Undistorted_SfM/", _defect_dir)
_dummy_dense_model = os.path.join(_dummy_base_dir, "Undistorted_SfM/", _defect_dir)
_dummy_indexes_dir = os.path.join(_dummy_base_dir, 'index/scene_info_0.1_0.7')

_output_dir = os.path.join(_data_dir, _defect_dir)
_database_path = os.path.join(_data_dir, _defect_dir, str(_defect_dir) + "_colmap.db")

"""
1. run init_sparse.py to generate
"""
args = ['python', 'init_sparse.py', '--data_dir', _data_dir, '--defect_dir', _defect_dir, '--img_dir', _img_dir,
        '--output_dir', _output_dir]
str_args = [str(x) for x in args]
subprocess.call(str_args)

""" 
2. run colmap feature_extractor
"""
'''
#subprocess.call(['colmap feature_extractor --image_path "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images/defect_1/rgb" --database_path "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images/defect_1/defect_1_colmap.db"'], shell=True)
_img_path = os.path.join(_data_dir, _defect_dir, _img_dir)
args = ['colmap', 'feature_extractor', '--image_path', _img_path, '--database_path', _database_path]
str_args = [str(x) for x in args]
subprocess.call(str_args)
'''

""" 
3. run colmap exhaustive_matcher
"""
'''
args = ['colmap', 'exhaustive_matcher', '--database_path', _database_path] #'--SiftMatching.max_ratio', 0.8
str_args = [str(x) for x in args]
subprocess.call(str_args)
'''
"""
4. run colmap point_triangulator
"""
'''
_triangulated_model = os.path.join(_output_dir, "triangulated")
os.mkdir(_triangulated_model)
args = ['colmap', 'point_triangulator', '--database_path', _database_path, '--image_path', _img_path, '--input_path',
        _output_dir, '--output_path', _triangulated_model]
str_args = [str(x) for x in args]
subprocess.call(str_args) #check cameras.txt ensure camera values are seperated by one space
'''
"""
5. run undistort_reconstructions.py
This is equivalent to running the following commands 5.1 and 5.2
"""
'''
### 5.1 run colmap image_undistorter
_undistorted_sparse = os.path.join(_output_dir, "undistorted_sparse")
args = ['colmap', 'image_undistorter', '--image_path', _img_path, '--input_path', _triangulated_model, '--output_path',
        _undistorted_sparse]
str_args = [str(x) for x in args]
subprocess.call(str_args)
'''
'''
### 5.2 run colmap model_converter
_undistorted_txt = os.path.join(_undistorted_sparse, 'sparse_txt')
os.mkdir(_undistorted_txt)
args = ['colmap', 'model_converter', '--input_path', os.path.join(_undistorted_sparse, 'sparse'), '--output_path',
        _undistorted_txt, '--output_type', 'TXT']
str_args = [str(x) for x in args]
subprocess.call(str_args)
'''
"""
6. pre_process_depth.py (only applicable to realsense)
"""
'''
# We need to put everything now in their proper directory (or dummy directory)
# _dummy_depth_dir = os.path.join(_dummy_base_dir, "/phoenix/S6/zl548/MegaDepth_v1/", _defect_dir, "dense0/depths")
# print(_dummy_base_dir+"/phoenix/S6/zl548/MegaDepth_v1/"+_defect_dir)
os.mkdir(_dummy_base_dir + "/phoenix/S6/zl548/MegaDepth_v1/" + _defect_dir)
# os.mkdir(os.path.join(_dummy_base_dir, "/phoenix/S6/zl548/MegaDepth_v1/", _defect_dir, "dense0")) #path.join is buggered
os.mkdir(_dummy_base_dir + "/phoenix/S6/zl548/MegaDepth_v1/" + _defect_dir + "/dense0")
os.mkdir(_dummy_base_dir + "/phoenix/S6/zl548/MegaDepth_v1/" + _defect_dir + "/dense0" + "/depths")
# os.makedirs(_dummy_depth_dir) # Permission error
args = ['python', 'pre_process_depth.py', '--data_path', _output_dir, '--output_path', _dummy_depth_dir]
str_args = [str(x) for x in args]
#subprocess.call(str_args) # don't do when get_depth_sfm is True

if get_depth_stereo:
        ### 6.5 colmap patch_match_stereo
        args = ['colmap', 'patch_match_stereo', '--workspace_path', _undistorted_sparse, '--workspace_format', 'COLMAP',
                '--PatchMatchStereo.geom_consistency', 'true', '--PatchMatchStereo.gpu_index', '0']
        str_args = [str(x) for x in args]
        subprocess.call(str_args)
        utils_misc.mv_bin_n_h5(os.path.join(_output_dir, 'undistorted_sparse', 'stereo', 'depth_maps'), _dummy_depth_dir, 3.5, True)
'''

os.makedirs(_dummy_depth_dir)
if get_depth_stereo:
        utils_misc.mv_bin_n_h5(os.path.join(_output_dir, 'dense', 'stereo', 'depth_maps'), _dummy_depth_dir)


"""
7. preprocess_scene.py
move dense_txt to os.path.join(_dummy_base_dir, "Undistorted_SfM/", _defect_dir)
where _dummy_base_dir = "/media/cviss3/Expansion/LoFTR_our_data/dummy_struct"
"""
shutil.copytree(_dense_dir, _dummy_dense_model)
args = ['python', 'preprocess_scene.py', '--base_path', _dummy_base_dir, '--scene_id', _defect_dir, '--output_path', _dummy_indexes_dir]
str_args = [str(x) for x in args]
subprocess.call(str_args)

"""
8. the_missing_link.py
"""
args = ['python', 'the_missing_link.py', '--input', os.path.join(_dummy_indexes_dir, _defect_dir + ".npz"), '--output',
        os.path.join(_dummy_indexes_dir, _defect_dir)]
str_args = [str(x) for x in args]
subprocess.call(str_args)
