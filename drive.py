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
from datetime import datetime
import select
import math
from PIL import ImageOps
from PIL import Image
from train import process_image, model
import live_stitcher

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
oshapeX = 320
oshapeY = 240
shapeX = 200
shapeY = 150
cshapeY = shapeY - shapeY // 3
num_reqs = 10
v_width = 16.
v_length = 24.
overlord_url = "http://192.168.2.16"
err_marrgin = 5
track_map = np.array([[[10,0],[10,150]],
    [[10,150],[61,193]],
    [[61,193],[96,159]],
    [[96,159],[96,75]],
    [[96,159],[150,200]],
    [[150,200],[200,160]],
    [[200,160],[200,70]],
    [[200,160],[240,190]],
    [[240,190],[280,150]],
    [[280,150],[280,74]],
    [[55,155],[55,70]],
    [[55,70],[98,22]],
    [[98,22],[145,59]],
    [[145,59],[145,160]],
    [[145,59],[200,17]],
    [[200,17],[245,70]],
    [[245,70],[245,154]],
    [[245,70],[280,20]],
    [[280,20],[320,86]],
    [[320,86],[320,200]]])

def parse_pckg(package):
	# Below is example:
	# CC block! sig: 12 (10 decimal) x: 127 y: 147 width: 91 height: 46 angle -1
	pos_x = package.find(" x: ")
	pos_y = package.find(" y: ", pos_x)
	pos_ye = package.find(" width: ", pos_y)
	pos_ang = package.find(" angle ", pos_ye)
	if pos_x < 0 or pos_y < 0 or pos_ye < 0 or pos_ang < 0:
		return -1, -1, 0
	x = int(package[pos_x + 4:pos_y])
	y = int(package[pos_y + 4:pos_ye])
	ang = int(package[pos_ang + 7:])
	if ang < 0:
		ang += 360
	return x, y, ang

def get_coords(num_reqs=num_reqs):

	x_lst = []
	y_lst = []
	ang_lst = []
	count = 0
	for i in range(num_reqs):
		try:
			r = urllib2.urlopen(overlord_url, timeout=1)
			package = r.read()

			if package == "NO DATA":
				if not x_lst:
					x, y, ang = -1, -1, 0
				else:
					x, y, ang = x_lst[-1], y_lst[-1], ang_lst[-1]
			else:
				x, y, ang = parse_pckg(package)

			if x < 0 or y < 0:
				count += 1
				continue
			x_lst.append(x)
			y_lst.append(y)
			ang_lst.append(ang)
		except:
			count += 1

	print(x_lst, y_lst, ang_lst, count)
	if count > num_reqs * 2 / 3:
		print("package was lost")
		return -1,-1,-1
	# x = np.argmax(np.bincount(x_lst))
	# y = np.argmax(np.bincount(y_lst))
	# ang = np.argmax(np.bincount(ang_lst))
	# print(x,y,ang)
	x = np.mean(x_lst)
	y = np.mean(y_lst)
	ang = np.mean(ang_lst)
	print(x,y,ang)
	return float(x), float(y), float(ang)

def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def check_position(track_map=track_map, width=v_width, length=v_length):
	x0, y0, ang = get_coords()
	if x0 < 0 or y0 < 0:
		return -1
	xsh = width * math.sin(math.radians(ang)) / 2.
	ysh = -width * math.cos(math.radians(ang)) / 2.
	x1 = x0 - length * math.cos(math.radians(ang))
	y1 = y0 + length * math.sin(math.radians(ang))
	for segment in track_map:
		if intersect((x0-xsh,y0-ysh), (x1+xsh, y1+ysh), segment[0], segment[1]):
			return 0
		if intersect((x0+xsh,y0+ysh), (x1-xsh, y1-ysh), segment[0], segment[1]):
			return 0
	return 1

def display_img():
	if not args.multi:
		test = subprocess.check_output(fetch_last_img, shell=True)
		img_name = args.st_dir + "/" + test.decode("utf-8").strip()
	else:
		####### get stitched image here
		img_name = live_stitcher.live_stitcher(args.st_dir)
		while img_name is None:
			img_name = live_stitcher.live_stitcher(args.st_dir)
		######

	# img = cv2.imread(img_name, 1)
	pil_img = Image.open(img_name)
	if type(pil_img) != type(None):
		pil_img = pil_img.crop((0, oshapeY // 3, oshapeX, oshapeY))
		pil_img = ImageOps.autocontrast(pil_img, 10)
		# image = load_img(path, target_size=shape)
		cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
		# img = cv2.equalizeHist(img)
		cv2.destroyAllWindows()
		cv2.imshow(img_name, cv_img)
		cv2.waitKey(1)
		return img_name
	print ("Error: couldn't get an image")
	return ""

def record_data(img_name, act_i):
	global correct
	# Record data on left/right turns and forwards command
	if act_i < 3:
		# if correct:
		# 	sa_lst.pop()
		# 	correct = False
		ts = time.time()
		st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
		new_name = st + "_" + img_name.split("/")[-1]
		print(img_name, new_name)
		sa_lst.append([new_name, act_i])
		shutil.copy(img_name, img_dir + new_name)
	# Erase data on reverse commands
	elif act_i < 6:
		# correct = True
		sa_lst.pop()

def send_control(act_i, img_name):
	global train
	try:
		print("Sending command %s" % links[act_i])
		# os.system(clinks[act_i])
		r = urllib2.urlopen(clinks[act_i], timeout=2)
		# print(r)
		if train and act_i < 6:
			record_data(img_name, act_i)
		return 0
	except:
		print("Command %s couldn't reach a vehicle" % clinks[act_i])
		return -1

def maunal_drive(img_name):

	res = 1 if not detect else check_position()
	if res == 0:
		print("Vehicle is out of bounds")
	elif res == -1:
		# If we cannot detect where we are
		print("Error: cannot identify position")
	getch.getch()
	key = getch.getch()
	for act_i in range(len(actions)):
		if key == actions[act_i]:
			res = send_control(act_i, img_name)
			break

def reverse_motion():
	last_command = sa_lst[-1][-1]
	block_lst[-1].append(last_command)
	inv_command = last_command + 3
	send_control(inv_command, img_name)

def auto_drive(img_name):

	res = 1 if not detect else check_position()
	if res == 1:
		# If we are in the right track
		if len(sa_lst) == len(block_lst):
			block_lst.append([])
		md_img, _ = process_image(img_name, None, False)
		pred_act = model.predict(np.array([md_img]))[0]
		print("Lft: %.2f | Fwd: %.2f | Rght: %.2f" % (pred_act[1], pred_act[0], pred_act[2]))
		act_i = np.argmax(pred_act)
		while pred_act[act_i] >= 0 and act_i in block_lst[-1]:
			pred_act[act_i] = -1.
			act_i = np.argmax(pred_act)
		if act_i == -1:
			block_lst.pop()
			reverse_motion()
		else:
			send_control(act_i, img_name)
		return pred_act, act_i
	elif res == -1:
		# If we cannot detect where we are
		print("Error: cannot identify position")
		return -1, -1
	else:
		# If we are outside
		try:
			reverse_motion()
		except:
			print("Error: cannot reverse an action")

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
		if (ct - ot) * 1000 > exp_time + 1200:
			drive = True

		if key == '\033':
			if auto:
				print("Autopilot disengaged")
				wait_time = 5
				auto = False
			if drive:
				drive = False
				maunal_drive(img_name)
				ot = ct
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
			drive = False
			pred_act, act_i = auto_drive(img_name)
			# print("Prediction angle: %.2f, %s" % (ang, links[act_i]))
			ot = ct
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
	parser.add_argument(
		'-detect',
		type=int,
		help='Turn detection module on - 1/ off - 0. Default:0',
		default=0
	)
	parser.add_argument(
		'-multi',
		type=int,
		help="Turn multi-cam function on - 1/ off - 0. Default:0",
		default=0
	)
	args = parser.parse_args()

	if os.path.exists(args.st_dir):
		fetch_last_img = "ls " + args.st_dir + " | tail -n1"
	else:
		print("Error: streaming directory %s doesn't exist" % args.st_dir)
		exit(1)

	auto = False
	if args.model:
		shape = (cshapeY, shapeX, 3)
		model = model(True, shape, tr_model=args.model)
		auto = args.auto
		err = 0

	train = False
	if args.train:
		train = True
		img_dir = "./data_sets/" + args.train + "/data/"
		data_dir = "./model_data/"
		if not os.path.exists(img_dir):
			os.makedirs(img_dir)
		# if not args.model:
		# 	model = model(load=False, shape)

	actions = ['A', 'D', 'C', 'B']
	links = ['/fwd', '/fwd/lf', '/fwd/rt', '/rev', '/rev/lf', '/rev/rt', '/exp' + str(args.exp_time)]
	clinks = [args.url + el for el in links]
	sa_lst = []
	block_lst = []
	detect = args.detect
	correct = False
	# Set expiration time for commands
	exp_time = args.exp_time
	if send_control(6, ""):
		print("Exiting")
		exit(0)

	drive(auto)
	if train:
		df = pd.DataFrame(sa_lst, columns=["img_name", "command"])
		df.to_csv(data_dir + args.train + '_log.csv', index=False)
