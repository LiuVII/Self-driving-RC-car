import serial
import time, datetime, glob, os, re, sys
import subprocess

argc = len(sys.argv)
if argc > 1:
        device = sys.argv[1]
else:
	#sometimes device is 14211
        device = '/dev/cu.usbmodem14311'

if argc > 2:
        baud = int(sys.argv[2])
else:
        baud = 9600

if argc > 3:
        fps = float(sys.argv[3])
else:
        fps = 5.

with serial.Serial(device, baud) as ser:
        ot = 0
        while True:
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')
                line = ser.readline().strip().decode("utf-8")
                if re.search("^[0-9]*\.?[0-9]+$", line):
                        if float(line) and ts - ot > 1./fps:
                                test = subprocess.check_output("ls -l data | tail -n1", shell=True)
                                test = test.decode("utf-8").strip()
                                data = re.search("(IMG.*\.jpg)$", test)
                                if data:
                                        f = data.group(1)
                                else:
                                        f = -1
                                print("%s, %s, %s"%(f, st, line))
                                ot = ts
