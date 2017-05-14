import serial
import time, datetime, glob, os, re
import subprocess

# port = '/dev/cu.usbmodem14211'

# ser = serial.Serial(port, 9600,timeout=5)
ot = 0

# go to data dir

while True:
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')
	# line = ser.readline().strip()
	if ts - ot > 0.2:
		test = subprocess.check_output("ls data | tail -n1", shell=True)
		# print(test)
		test = test.decode("utf-8").strip()
		data = re.search("(IMG.*\.jpg)$", test)
		if data:
			f = data.group(1)
		else:
			f = -1
	#	if glob.iglob('data/*.jpg'):
	#		f = max(glob.iglob('data/*.jpg'), key=os.path.getctime)
	#	else:
	#		f = -1
		# print("%s, %s, %s"%(f, st, line))
		print("%s, %s"%(f, st))
		ot = ts
