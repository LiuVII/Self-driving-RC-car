#!/bin/usr/env python3
import getch
import os
import sys
import time
import argparse
import urllib2
import subprocess
import cv2
import numpy as np
import pandas as pd
from math import pi
import shutil
# import threading
import select

from train import process_image, model

#Controls for wifi car v1
#pip3 install getch
#pip install https://pypi.python.org/packages/source/g/getch/getch-1.0-python2.tar.gz#\
#md5=586ea0f1f16aa094ff6a30736ba03c50

# up = '\033[A'
# down = '\033[B'
# right = '\033[C'
# left = '\033[D'
max_angle = pi / 4.0
key = 0
shapeX = 160
shapeY = 120

def record_data(img_name, act_i):
	sa_lst.append([img_name, act_i])
	shutil.copy(img_name, img_dir)

def display_img():
	test = subprocess.check_output(fetch_last_img, shell=True)
	img_name = args.st_dir + "/" + test.decode("utf-8").strip()
	img = cv2.imread(img_name, 1)
	if type(img) != type(None):
		cv2.destroyAllWindows()
		cv2.imshow(img_name, img)
		cv2.waitKey(1)
		return img_name
	print ("Error: couldn't get an image")
	return ""

def send_control(act_i):
	try:
		print("Sending command %s" % links[act_i])
		# os.system(clinks[act_i])
		urllib2.urlopen(clinks[act_i], timeout=2)
		return 0
	except:
		print("Command %s couldn't reach a vehicle" % clinks[act_i])
		return -1

def maunal_drive(img_name):

	getch.getch()
	key = getch.getch()	
	for act_i in range(len(actions)):
		if key == actions[act_i]:
			res = send_control(act_i)
			if train == True:
				record_data(img_name, act_i)
			break

def auto_drive(img_name):

	md_img, _ = process_image(img_name, None, False)
	pred_act = model.predict(np.array([md_img]))[0]
	print("Lft: %.2f | Fwd: %.2f | Rght: %.2f" % (pred_act[1], pred_act[0], pred_act[2]))
	act_i = np.argmax(pred_act)
	send_control(act_i)
	return pred_act, act_i

def	drive(auto):
	ot = 0
	wait_time = 0
	curr_auto = auto
	img_name = ""
	drive = False
	key = 0
	print("before thread")
	while True:
		while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			key = sys.stdin.read(1)
			if not key:
				exit(0)
		img_name = display_img()
		# print(img_name, curr_auto, drive)

		ct = time.time()
		if (ct - ot) * 1000 > exp_time * 4:
			drive = True
		
		if key == '\033':
			if auto:
				print("Autopilot disengaged")
				wait_time = 5
				auto = False
			if drive:
				maunal_drive(img_name)
				ot = ct
				drive = False
		# Exit command
		elif key == 'q':
			return
		elif key == 'a':
			auto = True
			print("Autopilot mode on!")
		elif key == 's':
			auto = False
			print("Autopilot disengaged")
		# If drive window is open and currently autopilot mode is on
		elif auto and drive and img_name:
			pred_act, act_i = auto_drive(img_name)
			# print("Prediction angle: %.2f, %s" % (ang, links[act_i]))
			ot = ct
			drive = False
			img_name = 0
		key = 0
		

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Driver')
	parser.add_argument(
		'-model',
		type=str,
		default='',
		help='Path to model h5 file. Model should be on the same path.'
	)
	parser.add_argument(
		'-auto',
		type=int,
		default=0,
		help='Autopilot mode on - 1/ off- 0. Default: 0.'
	)
	parser.add_argument(
		'-url',
		type=str,
		help='Url for connection. Default: http://192.168.2.3',
		default="http://192.168.2.3"
	)
	parser.add_argument(
		'-st_dir',
		type=str,
		help='Img stream directory. Default: st_dir',
		default="st_dir"
	)
	parser.add_argument(
		'-train',
		type=str,
		help='Name of the training set. Default: none',
		default=""
	)
	parser.add_argument(
		'-exp_time',
		type=int,
		help='Command expiration time. Default: 500ms',
		default=500
	)
	args = parser.parse_args()

	if os.path.exists(args.st_dir):
		fetch_last_img = "ls " + args.st_dir + " | tail -n1"
	else:
		print("Error: streaming directory %s doesn't exist" % args.st_dir)
		exit(1)
	
	auto = False
	if args.model:
		shape = (shapeX, shapeY, 3)
		model = model(True, shape, args.model)
		auto = args.auto
		err = 0

	train = False
	if args.train:
		train = True
		img_dir = "./data_sets/" + args.train + "/data/"
		data_dir = "./model_data/"
		if not os.path.exists(img_dir):
			os.makedirs(img_dir)

	actions = ['A', 'D', 'C', 'B']
	links = ['/fwd', '/fwd/lf', '/fwd/rt', '/rev', '/exp' + str(args.exp_time)]
	clinks = [args.url + el for el in links]
	sa_lst = []

	# Set expiration time for commands
	exp_time = args.exp_time
	if send_control(4):
		print("Exiting")
		exit(0)

	drive(auto)
	if train:
		df = pd.DataFrame(sa_lst, columns=["img_name", "command"])
		df.to_csv(data_dir + args.train + '_log.csv', index=False)
	