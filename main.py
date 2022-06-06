import subprocess
import os
import shutil

_data_dir = "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images"
_defect_dir = "defect_1"
_img_dir = "rgb"
_dummy_base_dir = "/media/cviss3/Expansion/LoFTR_our_data/dummy_struct"
_dummy_depth_dir = os.path.join(_dummy_base_dir, "/phoenix/S6/zl548/MegaDepth_v1/", _defect_dir, "dense0/depths")
_dummy_images_dir = os.path.join(_dummy_base_dir, "Undistorted_SfM/", _defect_dir)
_dummy_sparse_model = os.path.join(_dummy_base_dir, "Undistorted_SfM/", _defect_dir)
_dummy_indexes_dir = os.path.join(_dummy_base_dir, 'index/scene_info_0.1_0.7')

_output_dir = os.path.join(_data_dir, _defect_dir)
_database_path = os.path.join(_data_dir, _defect_dir, str(_defect_dir)+"_colmap.db")

### 1. run init_sparse.py to generate
args = ['python', 'init_sparse.py', '--data_dir', _data_dir, '--defect_dir', _defect_dir, '--img_dir', _img_dir, '--output_dir', _output_dir]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 2. run colmap feature_extractor
##subprocess.call(['colmap feature_extractor --image_path "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images/defect_1/rgb" --database_path "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images/defect_1/defect_1_colmap.db"'], shell=True)
_img_path = os.path.join(_data_dir, _defect_dir, _img_dir)
args = ['colmap', 'feature_extractor', '--image_path', _img_path, '--database_path', _database_path]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 3. run colmap exhaustive_matcher
args = ['colmap', 'exhaustive_matcher', '--database_path', _database_path]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 4. run colmap point_triangulator
_triangulated_model = os.path.join(_output_dir, "triangulated")
os.mkdir(_triangulated_model)
args = ['colmap', 'point_triangulator', '--database_path', _database_path, '--image_path', _img_path, '--input_path', _output_dir, '--output_path', _triangulated_model]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 5. undistort_reconstructions.py
### This is equivalent to running the following commands 5.1 and 5.2
### 5.1 run colmap image_undistorter
_undistorted_sparse = os.path.join(_output_dir, "undistorted_sparse")
args = ['colmap', 'image_undistorter', '--image_path', _img_path, '--input_path', _triangulated_model, '--output_path', _undistorted_sparse]
str_args = [str(x) for x in args]
subprocess.call(str_args)
### 5.2 run colmap model_converter
_undistorted_txt = os.path.join(_undistorted_sparse, 'sparse_txt')
os.mkdir(_undistorted_txt)
args = ['colmap', 'model_converter', '--input_path', os.path.join(_undistorted_sparse, 'sparse'), '--output_path', _undistorted_txt, '--output_type', 'TXT']
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 6. pre_process_depth.py
# We need to put everything now in their proper directory (or dummy directory)
#_dummy_depth_dir = os.path.join(_dummy_base_dir, "/phoenix/S6/zl548/MegaDepth_v1/", _defect_dir, "dense0/depths")
#print(_dummy_base_dir+"/phoenix/S6/zl548/MegaDepth_v1/"+_defect_dir)
os.mkdir(_dummy_base_dir+"/phoenix/S6/zl548/MegaDepth_v1/"+_defect_dir)
#os.mkdir(os.path.join(_dummy_base_dir, "/phoenix/S6/zl548/MegaDepth_v1/", _defect_dir, "dense0")) #path.join is buggered
os.mkdir(_dummy_base_dir+"/phoenix/S6/zl548/MegaDepth_v1/"+_defect_dir+"/dense0")
os.mkdir(_dummy_base_dir+"/phoenix/S6/zl548/MegaDepth_v1/"+_defect_dir+"/dense0"+"/depths")
#os.makedirs(_dummy_depth_dir) # Permission error
args = ['python', 'pre_process_depth.py', '--data_path', _output_dir, '--output_path', _dummy_depth_dir]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 7. preprocess_scene.py
# move sparse-txt at base_undistorted_sfm_path, scene_id, 'sparse-txt'
shutil.copytree(_undistorted_sparse, _dummy_sparse_model)
args = ['python', 'preprocess_scene.py', '--base_path', _dummy_base_dir, '--scene_id', _defect_dir, '--output_path', _dummy_indexes_dir]
str_args = [str(x) for x in args]
subprocess.call(str_args)

### 8. the_missing_link.py
args = ['python', 'the_missing_link.py', '--input', os.path.join(_dummy_indexes_dir, _defect_dir+".npz"), '--output', os.path.join(_dummy_indexes_dir, _defect_dir)]
str_args = [str(x) for x in args]
subprocess.call(str_args)