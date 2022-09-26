# Preparing Data for LoFTR
By: Max Midwinter (2022)

With Credit To: Mihai Dusmanu, Johannes L. Schoenberger and True Price

## Lidar Pipeline
Located in the sfm_free directory AKA the working directory

Create a folder called localization and git clone https://github.com/cviss-lab/localization to the folder

Run loftr_labelgen.py (change the data directory and project name to match)...

The concept is that for a scene we project 2d points to 3d then project the 3d points to the second image. 
We verify that the image coordinate is valid in the second image...


## SfM Pipeline
### Set Up
* Install Colmap 3.6+ 
  * By default, pip will install 3.4 which will not work...
    * Unless compiled Colmap from source there will be no CUDA. 
    GPU is required for Step 6.5 (match_match_stereo) which generates depth and 
    normal maps. 6.5 can take a very long time but can be skipped if depth maps
    are dense and of good quality.
  * Install Instructions: https://colmap.github.io/install.html
    * If you have difficulty installing ceres solver: https://brucknem.github.io/posts/install-ceres-solver/
    * If using older ceres solver consider: https://github.com/colmap/colmap/issues/1451 
### Extract Collected ROS Bags
* Get ROS bag from shared drive
* Launch on VM with dedicated ISO



### MISC. 
* Depending on the raw data format you may need some misc. functions to convert your data.
  You can find these in util.py
      
#### Notes
Real-sense RGB-D SLAM stereo reconstructed depth maps are not working.
Testing HL2 dataset