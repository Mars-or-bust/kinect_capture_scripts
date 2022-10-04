import pyaudio
import wave
import time

from multiprocessing import Process, Pipe
import platform
import multiprocessing

import subprocess
import os
import signal
import os
import time
import argparse
from datetime import date
import sys


def capture_audio(connection, save_filename, device_idx):
    # Set Parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    #RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = save_filename

    # SET THE DEVICE ID -> Kinects are [1,2] from AudioIDs.py


    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=device_idx)



    frames = []

    # Until the kill signal is sent
    sound_on = connection.recv()
    #print("* recording")

    while sound_on:
        # record 1 second of audio
        for i in range(0, int(RATE / CHUNK * 1)): 
            data = stream.read(CHUNK)
            frames.append(data)
        # check the signal
        if connection.poll():
            sound_on = False
            connection.recv()



    #print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    #print("Audio Saved")
    

## testing code
#if __name__ == "__main__":
#    if platform.system() == "Darwin":
#        multiprocessing.set_start_method('spawn')

#    data_save_dir = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\output.wav"

#    # set up the pipes for the processes to communicate with each other
#    parent, child = Pipe()

#    audio_thread = Process(target=capture_audio, args=(child,data_save_dir,1))
#    audio_thread.start()

#    time.sleep(0.5)
#    parent.send(True)

#    time.sleep(3)
#    parent.send(False)

    
