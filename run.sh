#!/bin/bash

cd "C:\Users\Vicon-OEM\Desktop\Kinect Scripts\env\Scripts"

# Fix the windows line endings 
sed -i 's/\r$//' activate

# Activate the environment
source activate

sleep 1
python "C:\Users\Vicon-OEM\Desktop\Kinect Scripts\initialize_cameras_w_sound.py"

