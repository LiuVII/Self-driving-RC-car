import os
import time
import sys
import numpy as np

# Init params
url = "rtsp://admin:20160404@192.168.2.13/onvif2"
time = 3600
fps = 20
outdir = "./st_dir"
outdir_sub = "/left"

## Param for output directory
argc = len(sys.argv)
if argc > 1:
	outdir = sys.argv[1]
if not os.path.exists(outdir):
	os.mkdir(outdir)
outdir_sub = outdir + outdir_sub
if not os.path.exists(outdir_sub):
	os.mkdir(outdir_sub)

## Param for fps
if argc > 2:
	fps = sys.argv[2]
	if float(fps) <= 0.0:
		print("Warning: FPS should be a rational number more than zero. Value set to 5")
		exit(0)

## Param for total training time
if argc > 3:
	time = sys.argv[3]
	if int(time) <= 0:
		print("Warning: Total time should be an integer more than zero. Value set to 3600")
		time = 3600

## Calculated number of zeros in filename counter
num = int(np.log10(int(time) * float(fps))) + 1

# Save images to the folder
command_str = "ffmpeg -i "+url+" -vf fps="+str(fps)+" '"+outdir_sub+"/IMG_%0"+str(num)+"d.jpg'"
print(command_str)
os.system(command_str)
exit(0)
