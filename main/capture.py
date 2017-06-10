from __future__ import print_function
import os, sys, re
import time, datetime
import numpy as np
import signal, atexit
from subprocess import Popen, PIPE, STDOUT
import argparse
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

url = ["rtsp://admin:20160404@192.168.2.13/onvif2", \
        "rtsp://admin:20160404@192.168.2.5/onvif2"]
# url = ["rtsp://admin:20160404@192.168.2.22/onvif2", \
#         "rtsp://admin:20160404@192.168.2.21/onvif2"]
outdir_sub = ["/left","/right"]
outdir_log = ["/left.log","/right.log"]

def ctrl_c_handler(signum, frame):
    print("\rStopping...           Time Elapsed: %s" % time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
    sys.exit(1)

def cleanup():
    global process_list
    try:
        for p in process_list:
            if not p.poll():
                p.terminate()
                p.wait()
        subprocess.Popen(['reset']).wait()
        process_list = []
    except:
        pass
    print("Stopped capturing...")

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-outdir',
        type=str,
        default='./st_dir',
        help="Output path"
    )
    parser.add_argument(
        '-fps',
        type=float,
        default=20.,
        help="FPS - number of frames to capture in 1 sec"
    )
    parser.add_argument(
        '-time',
        type=int,
        default=3600,
        help="Total training time"
    )
    return parser

if __name__ == "__main__":
    signal.signal(signal.SIGINT, ctrl_c_handler)
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
    	os.mkdir(args.outdir)
    outdir_sub = [args.outdir+x for x in outdir_sub]
    for x in outdir_sub:
        if not os.path.exists(x):
            os.makedirs(x)

    if args.fps <= 0.0:
        logging.error("Error: FPS should be a rational number more than zero.")
        exit(0)

    if args.time <= 0:
        logging.error("Error: Total time should be an integer more than zero.")
        exit(0)

    ## Calculated number of zeros in filename counter
    num = int(np.log10(int(args.time) * float(args.fps))) + 1
    logging.debug("Directory: %s" % args.outdir)
    logging.debug("FPS: %f" % args.fps)
    logging.debug("Time: %d" % args.time)
    logging.debug("Num: %d" % num)
    logging.debug("URL: %s" % str(url))

    command_list = []
    # Save images to the folder
    for i in range(len(url)):
        command_str = "ffmpeg -i "+url[i]+" -vf fps="+str(args.fps)+" '"+outdir_sub[i]+"/IMG_%0"+str(num)+"d.bmp' &> " + args.outdir+outdir_log[i]
        command_list.append(command_str)

    process_list = []
    atexit.register(cleanup)
    process_list = [Popen(cmd, shell=True) for cmd in command_list]
    print("Initializing...")
    start_time = time.time()
    time.sleep(5)
    print("Subprocesses Created:")
    print("Capture Folder: %s" % args.outdir)
    while True:
        # if re.search(r".*timed out.*", process_list[1].stdout.readline()) or\
        #     re.search(r".*timed out.*", process_list[0].stdout.readline()):
        #     print("Cameras Down")
        #     exit(0)
        for p in process_list:
            if p.poll():
                exit(1)
        print("\rCapturing...          Time Elapsed: %s" % time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)),end='\r')
    logging.error("Cameras Down")
    exit(0)
