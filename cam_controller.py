import subprocess
import os
import signal
import os
import time
import argparse
from datetime import date
import sys

from multiprocessing import Process, Pipe
import platform
import multiprocessing

import multiprocessing.pool
import functools

# Import the audio capture module
from audio_capture import *
from audio_wrap import wrap_audio

if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')


def cam_controller(connection, azure_kinect_sdk_path):
    """
    Starts/stops the cameras + kinect audio. Currently only setup for 2 cameras. 
    """
    # Minimize the camera terminal windows on startup
    SW_MINIMIZE = 6
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_MINIMIZE

    # change to the azure SDK directory
    os.chdir(azure_kinect_sdk_path)
    print(os.getcwd(),'\n')

    # Wait for the command from the main interface to start up the cameras and initialize audio
    cmd, terminate = connection.recv()

    cam1_save_path = cmd[0] + "\\" + cmd[1] + '_' + cmd[2] + "_cam1"
    cam2_save_path = cmd[0] + "\\" + cmd[1] + '_' + cmd[2] + "_cam2"

    ## Initialize the audio, it wont record until it recieves the start signal from this program
    audio_parent1, audio_child1 = Pipe()
    audio_parent2, audio_child2 = Pipe()

    # Start the main loop
    start_stop=True
    start_time = time.time()
    count = 0
    while not terminate:
        log = []

        # -l specifies the time, set to 15 when debugging
        cmd1 = "k4arecorder.exe --device 0 --external-sync sub -r 30 -c 720p -l 3600 " \
                  "--sync-delay 1 " + "\"" + cam1_save_path + ".mkv\""

        cmd2 = "k4arecorder.exe --device 1 --external-sync sub -r 30 -c 720p -l 3600 " \
               "--sync-delay 1 " + "\"" + cam2_save_path + ".mkv\""

        print(cmd1)

        if not start_stop:
            print("Ending Video Capture. Estimated Duration (Mins):", (time.time() - start_time)// 60)
            log.append("Ending Video Capture. Estimated Duration (Mins):  " +  str((time.time() - start_time)// 60))
            log.append('Save Directory: ' + cam1_save_path + ".mkv\"")
            all_cams_off = False
            while not all_cams_off:
                audio_parent1.send(False) # I THINK THIS THROWS AN ERROR FROM ITS RETURN CODE
                audio_parent2.send(False)
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    pass
                # STOP VIDEO CAPTURE
                # audio_thread1.join()
                # audio_thread2.join()
                try:
                    process1.send_signal(signal.CTRL_C_EVENT)
                    
                except:
                    pass

                try:
                    process2.send_signal(signal.CTRL_C_EVENT)
                    
                except:
                    #print('All Cameras Off.')
                    log.append('All Cameras Off.')

                all_cams_off = True

                #process1.join()
                #process2.join()


            start_stop = True

        connection.send(log)
        log = []

        if start_stop and count % 2 == 0: # Only start every other time the signal is sent
            sound_on = False
            log.append(cmd1)
            ON_POSIX = 'posix' in sys.builtin_module_names

            cam1_save_path = cmd[0] + "\\" + cmd[1] + '_' + cmd[2] + "_cam1"
            cam2_save_path = cmd[0] + "\\" + cmd[1] + '_' + cmd[2] + "_cam2"

            audio_save_path1 = cam1_save_path + ".wav"
            audio_save_path2 =  cam2_save_path + ".wav"

            audio_thread1 = Process(target=capture_audio, args=(audio_child1, audio_save_path1, 1))
            audio_thread1.start()

            audio_thread2 = Process(target=capture_audio, args=(audio_child2, audio_save_path2, 2))
            audio_thread2.start()

            log.append(audio_save_path1)

            process1 = subprocess.Popen(cmd1,
                                        stdout=subprocess.PIPE,
                                        # stdin=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        shell=False,
                                        startupinfo=info)


            time.sleep(0.1)
            #print('Camera 1 ready in subordinate mode')
            #for i in range(0,4):
            #    log.append(process1.stdout.readline().decode("utf-8"))
            #log.append('Camera 1 ready in subordinate mode')

            
            # cmd = "k4arecorder.exe --device 1 --external-sync sub -r 30 -l 15 --sync-delay 1 \"C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\cam2.mkv\""

            process2 = subprocess.Popen(cmd2,
                                        stdout=subprocess.PIPE,
                                        # stdin=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        shell=False,
                                        startupinfo=info)

            #print('Camera 2 ready in subordinate mode')
            log.append('Cameras ready in subordinate mode')

            # update the main programs logs
            connection.send(log)
            log = []
            time.sleep(0.1)

            # THIS LINE BLOCKS IN ORDER TO WAIT TO START AUDIO CAPTURE
            for i in range(0,5):
                line = process1.stdout.readline().decode("utf-8")
                print(line)
                log.append(line)
     

            # START AUDIO CAPTURE
            audio_parent1.send(True)
            audio_parent2.send(True)
            print("AUDIO CAPTURE ENGAGED")
            log.append("AUDIO CAPTURE ENGAGED")
            count +=1

            # SEND A SIGNAL TO THE INTERFACE THAT RECORDING IS IN PROGRESS
            connection.send(log)

            start_stop = False

        cmd, terminate = connection.recv()
        #start_stop = False


    # Do one last check to ensure the cameras are off
    try:
        process1.send_signal(signal.CTRL_C_EVENT)
    except:
        pass

    try:
        process2.send_signal(signal.CTRL_C_EVENT)
    except:
        all_cams_off = True
        print('All Cameras Off.')

    # Check the AUDIO stream
    time.sleep(2)
    try: 
        audio_parent1.send(False)
    except:
        pass
    try: 
        audio_parent2.send(False)
    except:
        print('All Audio Off.')

    print("Subprocesses exited gracefully")