import os
import subprocess
from multiprocessing import Process, Pipe

audio_path = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\Sep-30-2021\\cam1_TRAINING_1.wav"
video_path = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\Sep-30-2021\\cam1_TRAINING_1.mkv"



def wrap_audio(vid_name):
    """
    Wraps audio into the Kinect MKV file with the color and depth info. 
    """
    old_dir = os.getcwd()
    os.chdir("C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts")
    # for adding sound to an existing mkv
    vid_name = os.path.abspath(vid_name).split('.')[0]
    #cmd = '.\\ffmpeg -i "Sep-30-2021\\cam1_TRAINING_1.mkv" -i "Sep-30-2021\\cam1_TRAINING_1.wav" -c:v copy -c:a aac test3.mkv'
    cmd = '.\\ffmpeg -i "{a}.mkv" -i "{a}.wav" -c:v copy -c:a aac -y "{a}_w_audio.mkv"'.format(a=vid_name)
    print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # for turning into an MP$
    #cmd = '.\\ffmpeg -i "Sep-30-2021\\cam1_TRAINING_1.mkv" -map 0:v:0 -pix_fmt yuv420p -y test.mp4'
    os.chdir(old_dir)

    return vid_name.split('.')[0] + "_w_audio.mkv"


if __name__ == "__main__":
    #wrap_audio("C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\Sep-30-2021\\TRAINING_1_cam1")
    wrap_audio("C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\OCT-01-2021\\TRAINING_1_cam2")