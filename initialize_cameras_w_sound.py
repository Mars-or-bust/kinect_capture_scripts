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

import multiprocessing.pool
import functools

# My imports
from cam_controller import *
from interface_recording import *
#from interface_annotation import *


'''
def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

@timeout(0.01)
def activate_sound(proc):
    return proc.stdout.readline()

@timeout(0.01)
def terminate_main(connection):
    cmd, terminate = connection.recv()
    return terminate
'''



if __name__ == "__main__":
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')

    azure_body_tracking_sdk = "C:\\Program Files\\Azure Kinect Body Tracking SDK\\tools\\"
    azure_kinect_sdk = "C:\\Program Files\\Azure Kinect SDK v1.4.1\\tools\\"
    data_save_dir = "G:\\Gavin's Study\\example_subject\\test_session"

    # set up the pipes for the processes to communicate with each other
    parent, child = Pipe()

    vid_thread = Process(target=cam_controller, args=(parent,azure_kinect_sdk))
    vid_thread.start()

    root = tk.Tk()
    app = Application(master=root,connection=child,data_save_dir=data_save_dir)
    app.mainloop()








