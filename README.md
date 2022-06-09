# Preparing Data for LoFTR
By: Max Midwinter (2022)

With Credit To: Mihai Dusmanu, Johannes L. Schoenberger and True Price

## Set Up
* Install Colmap 3.6+ 
  * By default, pip will install 3.4 which will not work...
    * Unless compiled Colmap from source there will be no CUDA. 
    GPU is required for Step 6.5 (match_match_stereo) which generates depth and 
    normal maps. 6.5 can take a very long time but can be skipped if depth maps
    are dense and of good quality.
  * Install Instructions: https://colmap.github.io/install.html
    * If you have difficulty installing ceres solver: https://brucknem.github.io/posts/install-ceres-solver/

## Extract Collected ROS Bags
* Get ROS bag from shared drive
* Launch on VM with dedicated ISO

## Run main.py
* set to appropriate paths 
``` python
_data_dir = "/media/cviss3/Expansion/21-06-06 gardiner intel realsense/images"
_defect_dir = "defect_1"
_img_dir = "rgb"
_dummy_base_dir = "/media/cviss3/Expansion/LoFTR_our_data/dummy_struct"
```
* get Max's Expansion Drive 
* Run main.py

## MISC. 
* Depending on the raw data format you may need some misc. functions to convert your data.
  You can find these in util.py
      
