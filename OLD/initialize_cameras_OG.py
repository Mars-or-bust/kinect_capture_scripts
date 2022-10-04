#!usr/bin/env python

import subprocess
import os
# import pyglet
import keyboard
import signal
import os
import time



azure_body_tracking_sdk = "C:\\Program Files\\Azure Kinect Body Tracking SDK\\tools\\"
azure_kinect_sdk = "C:\\Program Files\\Azure Kinect SDK v1.4.1\\tools\\"

data_save_dir = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\"





#def main():

os.chdir(azure_kinect_sdk)
print(os.getcwd(),'\n')

cmd = "k4arecorder.exe --device 0 --external-sync sub -r 30 -l 15 --sync-delay 1 \"C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\cam1.mkv\""
process1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
print('Camera 1 ready in subordinate mode')

cmd = "k4arecorder.exe --device 1 --external-sync sub -r 30 -l 15 --sync-delay 1 \"C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\cam2.mkv\""
process2 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
print('Camera 2 ready in subordinate mode')

cams_on = True
while cams_on is True:
    try:
        if keyboard.read_key() == "q":
            print("Ending Video Capture")
            #Terminate the processes
            #terminate(process1)
            #terminate(process2)
            process1.send_signal(signal.CTRL_C_EVENT)
            process2.send_signal(signal.CTRL_C_EVENT)
            # check if they are still alive
            cams_on = False
    except:
        continue

# Add a delayt
if process1.Popen.poll() is not None():
    print("Cam1 Shutdown")

print("Capture complete")



#if __name__ == "__main__":
#    main()

