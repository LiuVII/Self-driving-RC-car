import os
import time
import sys
import numpy as np

# Init params
url = ["rtsp://admin:20160404@192.168.2.13/onvif2", \
        "rtsp://admin:20160404@192.168.2.5/onvif2"]
time = 3600
fps = 5
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
	time = sys.argv[3]
	if int(time) <= 0:
		print("Warning: Total time should be an integer more than zero. Value set to 3600")
		time = 3600

## Calculated number of zeros in filename counter
num = int(np.log10(int(time) * float(fps))) + 1

# Save images to the folder
# command_str = "ffmpeg -i "+url+" -vf fps="+str(fps)+" '"+outdir+"/IMG_%0"+str(num)+"d.jpg'"
command_str = "ffmpeg"
if len(url) != len(outdir_sub):
    print "number of input does not match number of output"
    exit(1)
for i in url:
    command_str += " -i " + i
count = 0
for i in outdir_sub:
    command_str += " -map " + str(count)
    command_str += " -vf fps=" + str(fps)
    command_str += " '" + i + "/IMG_%0" +str(num)+"d.jpg'"
    count += 1

print(command_str)
os.system(command_str)
exit(0)
