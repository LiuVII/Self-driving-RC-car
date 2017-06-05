from __future__ import print_function
import os
import time
import datetime
import sys
import numpy as np
import signal
import atexit
from subprocess import Popen, PIPE, STDOUT
import subprocess

def ctrl_c_handler(signum, frame):
    print ("\rStopping capture...")
    sys.exit(1)

def cleanup():
    global process_list
    for p in process_list:
        p.communicate(input=b'q\n')
        if not p.poll():
            p.kill()
    process_list = []
    print("Stopped capturing...")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, ctrl_c_handler)
    url = ["rtsp://admin:20160404@192.168.2.13/onvif2", \
            "rtsp://admin:20160404@192.168.2.5/onvif2"]
    time_last = 3600
    fps = 20
    outdir = "./st_dir"
    outdir_sub = ["/left","/right"]

    ## Param for output directory
    argc = len(sys.argv)
    if argc > 1:
    	outdir = sys.argv[1]
    if not os.path.exists(outdir):
    	os.mkdir(outdir)
    outdir_sub = [outdir+x for x in outdir_sub]
    for x in outdir_sub:
        if not os.path.exists(x):
            os.mkdir(x)

    ## Param for fps
    if argc > 2:
    	fps = sys.argv[2]
    	if float(fps) <= 0.0:
    		print("Warning: FPS should be a rational number more than zero. Value set to 5")
    		exit(0)

    ## Param for total training time
    if argc > 3:
    	time_last = sys.argv[3]
    	if int(time_last) <= 0:
    		print("Warning: Total time should be an integer more than zero. Value set to 3600")
    		time_last = 3600

    ## Calculated number of zeros in filename counter
    num = int(np.log10(int(time_last) * float(fps))) + 1

    command_list = []
    # Save images to the folder
    for i in range(len(url)):
        command_str = "ffmpeg -i "+url[i]+" -vf fps="+str(fps)+" '"+outdir_sub[i]+"/IMG_%0"+str(num)+"d.jpg'"
        command_list.append(command_str)

    process_list = []
    atexit.register(cleanup)
    process_list = [Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT) for cmd in command_list]
    print("subprocesses created")
    print("Capture Folder: %s" % outdir)
    start_time = time.time()
    while True:
        print("\rCapturing... Time Elapsed: %s" % time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)),end='\r')
    exit(0)
