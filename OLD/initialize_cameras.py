#!usr/bin/env python

import subprocess
import os
import signal
import os
import time
import argparse
from datetime import date
import sys

import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import scrolledtext

from multiprocessing import Process, Pipe
import platform
import multiprocessing

import cam_controller


azure_body_tracking_sdk = "C:\\Program Files\\Azure Kinect Body Tracking SDK\\tools\\"
azure_kinect_sdk = "C:\\Program Files\\Azure Kinect SDK v1.4.1\\tools\\"
data_save_dir = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\"

# os.chdir(azure_kinect_sdk)

def main(connection):

    SW_MINIMIZE = 6
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_MINIMIZE

    os.chdir(azure_kinect_sdk)
    print(os.getcwd(),'\n')

    cmd, terminate = connection.recv()

    start_stop=True
    start_time = time.time()
    while not terminate:
        log = []

        cmd1 = "k4arecorder.exe --device 0 --external-sync sub -r 30 -l 15 " \
                  "--sync-delay 1 \"" + cmd[0] + "\\cam1_" + \
                  cmd[1] + '_' + cmd[2] + ".mkv\""

        cmd2 = "k4arecorder.exe --device 1 --external-sync sub -r 30 -l 15 " \
               "--sync-delay 1 \"" + cmd[0] + "\\cam2_" + \
               cmd[1] + '_' + cmd[2] + ".mkv\""

        if not start_stop:
            print("Ending Video Capture. Estimated Duration (Mins):", (time.time() - start_time)// 60)
            log.append("Ending Video Capture. Estimated Duration (Mins):  " +  str((time.time() - start_time)// 60))
            log.append('Save Directory: ' + "\"" + cmd[0] + "\\cam1_" + cmd[1] + '_' + str(int(cmd[2])-1) + ".mkv\"")
            all_cams_off = False
            while not all_cams_off:
                try:
                    process1.send_signal(signal.CTRL_C_EVENT)
                except:
                    pass

                try:
                    process2.send_signal(signal.CTRL_C_EVENT)
                except:
                    all_cams_off = True
                    print('All Cameras Off. Resetting...')
                    log.append('All Cameras Off. Resetting...')

            start_stop = True

        connection.send(log)
        log = []

        if start_stop:
            log.append(cmd1)
            process1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            time.sleep(0.1)
            print('Camera 1 ready in subordinate mode')
            log.append('Camera 1 ready in subordinate mode')

            
            # cmd = "k4arecorder.exe --device 1 --external-sync sub -r 30 -l 15 --sync-delay 1 \"C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\cam2.mkv\""

            process2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            print('Camera 2 ready in subordinate mode')
            log.append('Camera 2 ready in subordinate mode')


        connection.send(log)
        cmd, terminate = connection.recv()
        start_stop = False

        # cams_on = True
        # while cams_on is True:
        #     try:
        #         if not start_stop:
        #             print("Ending Video Capture")
        #             # #Terminate the processes
        #             # try:
        #             #     process1.send_signal(signal.CTRL_C_EVENT)
        #             # except:
        #             #     pass
        #             #
        #             # try:
        #             #     process2.send_signal(signal.CTRL_C_EVENT)
        #             # except:
        #             #     print('All Cameras Off')
        #             # check if they are still alive
        #             cams_on = False
        #         else:
        #             time.sleep(0.1)
        #     except:
        #         continue

    try:
        process1.send_signal(signal.CTRL_C_EVENT)
    except:
        pass

    try:
        process2.send_signal(signal.CTRL_C_EVENT)
    except:
        all_cams_off = True
        print('All Cameras Off. Resetting...')

    print("Subprocesses exited gracefully")




class Application(tk.Frame):
    def __init__(self, master=None, connection=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('520x350') # adjust window size here
        self.master.title("Kinect Camera Recorder")
        self.grid(column=0, row=0, padx=10, pady=2, sticky="W")

        # Initialize starting trial name and save directory
        self.trial_name = "TRAINING"
        self.save_dir = data_save_dir + date.today().strftime("%b-%d-%Y")
        self.trial_number=""

        # Initialize the status of the cams and trial to off, set to true when the first capture starts
        self.trial_status = False
        # self.cams_on = True
        self.terminate = False

        self.connection = connection

        self.create_widgets()

    def create_widgets(self):
        # Prompt the user for the Trial Name
        self.trial_name_desc = tk.Label(self, text="Enter Trial Name:")
        self.trial_name_desc.grid(column=0, row=0, padx=2,pady=2,sticky="W")

        # set up a frame to store the entry and auto increment fields
        self.trial_frame = tk.Frame(self)
        self.trial_frame.grid(column=1, row=0, padx=0,pady=2,sticky="W")

        self.trial_name_entry = tk.Entry(self.trial_frame,text=self.trial_name)
        self.trial_name_entry.grid(column=0, row=0, padx=0,pady=2,sticky="W")
        # self.trial_name_ext = tk.Label(self, text=".mkv")
        # self.trial_name_ext.grid(column=2, row=0, padx=0,pady=2)

        # Checkbox for autoincrement
        self.auto_incr = tk.IntVar()
        self.auto_incr_box = tk.Checkbutton(self.trial_frame, text='Auto Increment',
                                            variable=self.auto_incr,
                                            onvalue=1, offvalue=0)#,
                                            #command=self.auto_incr_status)
        self.auto_incr_box.select()
        self.auto_incr_box.grid(column=1, row=0, padx=0, pady=2, sticky="W")

        # BUTTON to specify the save directory
        self.chg_save_dir = tk.Button(self,fg="black",
                                      text="Change Save Dir",
                                      command=self.get_save_dir)
        self.chg_save_dir.grid(column=0, row=1, padx=2,pady=2,sticky="W")
        # self.chg_save_dir["command"] = self.get_save_dir
        self.chg_save_dir_lbl = tk.Label(self, text=self.save_dir)
        self.chg_save_dir_lbl.grid(column=1, row=1, padx=0, pady=2,sticky="W")

        # BUTTON for intitializing the camera capture
        self.start_stop_button = tk.Button(self,fg="black",
                                     text="Initialize\n Cameras",
                                     font=("Ariel",20),
                                     height = 4,
                                     width=20,
                                     bg='white',
                                     command=self.check_status)
        self.start_stop_button.grid(column=0, columnspan=3, row=3, padx=2,pady=2,sticky="W")


        # POWER OFF BUTTON
        self.quit = tk.Button(self, text="Power Off", fg="red",
                              command=self.quit_button)
        self.quit.grid(column=2, row=0, padx=0,pady=2,sticky="e")

        # SHELL OUTPUT
        self.text_area = scrolledtext.ScrolledText(self,
                                                   wrap=tk.WORD,
                                                   #width=70,
                                                   height=8,
                                                   font=("Times New Roman",9),
                                                   bg='#f1f1f1')
        self.text_area.grid(column=0, columnspan=4, row=4, padx=2,pady=2,sticky="W")
        self.text_area.insert('end','')

    def get_save_dir(self):
        self.save_dir = filedialog.askdirectory()
        self.chg_save_dir_lbl['text'] = self.save_dir

    def quit_button(self):
        self.terminate = True
        self.connection.send((("","",""), self.terminate))
        self.master.destroy()


    def check_status(self):
        # if not self.cams_on:
        #     self.cams_on = True

        # else:
        #     # check if they are still alive
        #     self.start_stop_button['text'] = "Status: Saving video"
        #     self.start_stop_button['bg'] = "red"
        #     self.master.update_idletasks()
        #
        #     time.sleep(1)
        #
        #     self.cams_on=False

        self.start_stop_button['text']="Status: Initializing video"
        self.start_stop_button['bg']="yellow"
        self.master.update_idletasks()
        time.sleep(2)

        self.init_cmd()


        # print(self.cmd)

        self.connection.send((self.cmd, self.terminate))

        # First update
        for i in self.connection.recv():
            self.text_area.insert('end', '\n' + i)

        self.start_stop_button['text']="Status: Offline\nResetting Cameras"
        self.start_stop_button['bg']="red"
        self.master.update_idletasks()
        time.sleep(2)

        # Second update
        for i in self.connection.recv():
            self.text_area.insert('end', '\n' + i)

        self.start_stop_button['text'] = "Status: Active\n(Press to Stop Recording)"
        self.start_stop_button['bg'] = "green"
        self.master.update_idletasks()



    def init_cmd(self):
        """Initializes the cameras and syncs them to the master controller."""


        # Get the text entry for the trial name if there is one
        if self.trial_name_entry.get().strip() is not "":
            trial_name = self.trial_name_entry.get()
            # Update the system count for new trial names
            if self.trial_name != trial_name:
                # If there is a name change consider it a new trial

                # check to see if there are integers at the end
                try:
                    self.trial_number = int(trial_name.split('_')[-1]) -1
                    self.trial_name = trial_name.split('_')[0]

                except:
                    self.trial_name = trial_name
                    self.trial_number = -1
                    self.trial_status = False

        # check auto increment status
        if self.auto_incr.get() == 1:
            if self.trial_status:
                self.trial_number += 1
            else:
                self.trial_number = 1
        else:
            self.trial_number = ""

        self.trial_status = True

        # self.cmd = "k4arecorder.exe --device 0 --external-sync sub -r 30 -l 15 " \
        #       "--sync-delay 1 \"" + self.save_dir + "\\cam1_" + \
        #       self.trial_name + '_' + str(self.trial_number) + ".mkv\""


        self.cmd = (self.save_dir, self.trial_name, str(self.trial_number))

        os.makedirs(self.save_dir,exist_ok=True)



        # print("Capture complete:",
        #       '\t' + self.save_dir + "\\cam1_" + self.trial_name + '_' + str(self.trial_number) + ".mkv",
        #       '\n\t\t\t\t\t' + self.save_dir + "\\cam2_" + self.trial_name + '_' + str(self.trial_number) + ".mkv")




if __name__ == "__main__":
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')

    # set up the pipes for the processes to communicate with each other
    parent, child = Pipe()

    vid_thread = Process(target=main, args=(parent,))
    vid_thread.start()

    root = tk.Tk()
    app = Application(master=root,connection=child)
    app.mainloop()








