
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

import multiprocessing.pool
import functools

import video_annotation

class Application(tk.Frame):
    def __init__(self, master=None, connection=None, data_save_dir=None):
        super().__init__(master)
        self.master = master
        self.master.geometry('520x350') # adjust window size here
        self.master.title("Kinect Camera Recorder")
        self.grid(column=0, row=0, padx=10, pady=2, sticky="W")

        # Initialize starting trial name and save directory
        self.trial_name = tk.StringVar(self.master, "TRAINING")
        self.save_dir = data_save_dir #+ date.today().strftime("%b-%d-%Y")
        self.trial_number=""

        # Initialize the status of the cams and trial to off, set to true when the first capture starts
        self.trial_status = False
        # self.cams_on = True
        self.terminate = False
        self.cam_status = False # Cam status is initializes to off

        self.connection = connection

        self.create_widgets()

    def create_widgets(self):
        # Prompt the user for the Trial Name
        self.trial_name_desc = tk.Label(self, text="Enter Trial Name:")
        self.trial_name_desc.grid(column=0, row=0, padx=2,pady=2,sticky="W")

        # set up a frame to store the entry and auto increment fields
        self.trial_frame = tk.Frame(self)
        self.trial_frame.grid(column=1, row=0, padx=0,pady=2,sticky="W")

        self.trial_name_entry = tk.Entry(self.trial_frame,text=self.trial_name, textvariable=self.trial_name)
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
        self.auto_incr_box.grid(column=1, columnspan=2, row=0, padx=0, pady=2, sticky="W")

        # BUTTON to specify the save directory
        self.chg_save_dir = tk.Button(self,fg="black",
                                      text="Change Save Dir",
                                      command=self.get_save_dir)
        self.chg_save_dir.grid(column=0, row=1, padx=2,pady=2,sticky="W")
        # self.chg_save_dir["command"] = self.get_save_dir
        self.chg_save_dir_lbl = tk.Label(self, text=self.save_dir, font=("Ariel",10))
        self.chg_save_dir_lbl.grid(column=1, columnspan=3, row=1, padx=0, pady=2,sticky="w")

        # BUTTON for intitializing the camera capture
        self.start_stop_button = tk.Button(self,fg="black",
                                     text="Initialize\nCameras",
                                     font=("Ariel",16),
                                     height = 4,
                                     width=16,
                                     bg='white',
                                     command=self.check_status)
        self.start_stop_button.grid(column=0, columnspan=2, row=3, padx=2,pady=2,sticky="W")

        # BUTTON for intitializing the camera capture
        self.annotations_button = tk.Button(self,fg="black",
                                     text="Annotate\nClip",
                                     font=("Ariel",14),
                                     height = 4,
                                     width=16,
                                     bg='white',
                                     command=self.annotate)
        self.annotations_button.grid(column=1, columnspan=2, row=3, padx=2,pady=2,sticky="e")


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

        self.init_cmd()

        if not self.cam_status:

            self.start_stop_button['text']="Status: Offline\nResetting Cameras"
            self.start_stop_button['bg']="red"
            self.master.update_idletasks()

            time.sleep(1)

            # print(self.cmd)

            self.connection.send((self.cmd, self.terminate))

            # First update
            for i in self.connection.recv(): # THE ERROR OCCURS HERE
                self.text_area.insert('end', '\n' + i)

            self.start_stop_button['text']="Status:\nInitializing video"
            self.start_stop_button['bg']="yellow"
            self.master.update_idletasks()

            # Second update
            for i in self.connection.recv():
                self.text_area.insert('end', '\n' + i)

            self.start_stop_button['text'] = "Status: Ready"
            self.start_stop_button['bg'] = "cyan"
            self.master.update_idletasks()

            # Second update
            for i in self.connection.recv():
                self.text_area.insert('end', '\n' + i)

            self.start_stop_button['text'] = "Status: Recording\n(Click to End)"
            self.start_stop_button['bg'] = "green"
            self.master.update_idletasks()

            self.cam_status = True
        else:
            self.connection.send((self.cmd, self.terminate))
            self.start_stop_button['text']="Initialize\nCameras"
            self.start_stop_button['bg']="white"
            self.master.update_idletasks()
            self.cam_status = False
            

    def init_cmd(self):
        """Initializes the cameras and syncs them to the master controller."""


        # Get the text entry for the trial name if there is one
        if self.trial_name_entry.get().strip() != "":
            trial_name = self.trial_name_entry.get()
            # Update the system count for new trial names
            if self.trial_name != trial_name:
                # If there is a name change consider it a new trial

                # check to see if there are integers at the end
                #try:
                #    self.trial_number = int(trial_name.split('_')[-1]) -1
                #    self.trial_name = trial_name.split('_')[0]

                #except:
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

    def annotate(self):
        annotation_file = filedialog.askopenfilename()
        #print(os.getcwd())
        #cmd = "python video_annotation.py --save_path \"{}\"".format(annotation_file)
        #print(cmd)
        #subprocess.run(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

        video_annotation.main(annotation_file)

        



if __name__ == "__main__":
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')

    azure_body_tracking_sdk = "C:\\Program Files\\Azure Kinect Body Tracking SDK\\tools\\"
    azure_kinect_sdk = "C:\\Program Files\\Azure Kinect SDK v1.4.1\\tools\\"
    data_save_dir = "C:\\Users\\Vicon-OEM\\Desktop\\Kinect Scripts\\"

    # set up the pipes for the processes to communicate with each other
    parent, child = Pipe()

    root = tk.Tk()
    app = Application(master=root,connection=child,data_save_dir=data_save_dir)
    app.mainloop()