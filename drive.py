#!/bin/usr/env python3
import getch
import os
import time
import argparse
import urllib2
import subprocess
import cv2

from train import process_image, model

#Controls for wifi car v1
#pip3 install getch
#pip install https://pypi.python.org/packages/source/g/getch/getch-1.0-python2.tar.gz#\
#md5=586ea0f1f16aa094ff6a30736ba03c50

# up = '\033[A'
# down = '\033[B'
# right = '\033[C'
# left = '\033[D'

def display_img():
	test = subprocess.check_output(fetch_last_img, shell=True)
	img_name = args.data_dir + "/" + test.decode("utf-8").strip()
	img = cv2.imread(img_name, 1)
	if type(img) != type(None):
		cv2.destroyAllWindows()
		cv2.imshow(img_name, img)
		cv2.waitKey(1)
		return img_name
	print ("Error: couldn't get an image")
	return 0

def send_control(act_i):
	try:
		print("Sending command %s" % links[act_i])
		# os.system(clinks[act_i])
		r = urllib2.urlopen(clinks[act_i], timeout=1)
	except:
		print("Command %s couldn't reach a vehicle" % clinks[act_i])

def maunal_drive():

	getch.getch()
	key = getch.getch()	
	for act_i in range(len(actions)):
		if key == actions[act_i]:
			send_control(act_i)
			break

def auto_drive(img_name):

	md_img, _ = process_image(img_name, None, False)
	pred_angle = model.predict(np.array([md_img]))[0][0]
	if pred_angle >= max_angle // 2:
		act_i = 2
		if pred_angle > max_angle:
			pred_angle = max_angle
	elif pred_angle <= -max_angle // 2:
		act_i = 1
		if pred_angle < -max_angle:
			pred_angle = -max_angle
	else:
		act_i = 0
	send_control(act_i)
	return pred_angle

def	drive(auto):
	ot = 0
	wait_time = 0
	curr_auto = auto
	img_name = 0

	while True:

		img_name = display_img()

		if wait_time <= 0:
			if curr_auto != auto:
				print("Autopilot mode on!")
			curr_auto = auto

		ct = time.time()
		key = getch.getch()
		
		if ct - ot > 1:
			drive = True
			if wait_time > 0:
				wait_time -= 1
		
		if key == '\033':
			if curr_auto:
				print("Autopilot disengaged")
				wait_time = 2
				curr_auto = 0
			if drive:
				maunal_drive()
				ot = ct
				drive = False
		# If drive window is open and currently autopilot mode is on
		elif curr_auto and drive and img_name:
			auto_drive(img_name)
			ot = ct
			drive = False
			img_name = 0
		# Exit command
		elif key == 'q':
			exit(0)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Driver')
	parser.add_argument(
		'-model',
		type=str,
		default='',
		help='Path to model h5 file. Model should be on the same path.'
	)
	parser.add_argument(
		'-url',
		type=str,
		help='Url for connection. Default: http://10.10.10.112',
		default="http://10.10.10.112"
	)
	parser.add_argument(
		'-data_dir',
		type=str,
		help='Img stream directory. Default: st_data',
		default="st_data"
	)
	args = parser.parse_args()

	if os.path.exists(args.data_dir):
		fetch_last_img = "ls " + args.data_dir + " | tail -n1"
	else:
		print("Error: streaming directory %s doesn't exist" % args.data_dir)
		exit(1)
	
	auto = False
	if args.model:
		shape = (100, 100, 3)
		model = model(True, shape, args.model)
		auto = True
		err = 0

	actions = ['A', 'D', 'C', 'B']
	links = ['/fwd', '/fwd/lt', '/fwd/rt', '/rev']
	# clinks = ['curl '+ args.url + el for el in links]
	clinks = [args.url + el for el in links]
	
	drive(auto)
	