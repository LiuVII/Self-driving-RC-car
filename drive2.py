#!/bin/usr/env python3
import pygame
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
# from train import process_image, model
from train2 import process_image, model
import live_stitcher


delta_time = -100
mult_sh=2
oshapeX = 640
oshapeY = 240
w = oshapeX*mult_sh
h = oshapeY*mult_sh
NUM_CLASSES = 4
shapeX = 320
shapeY = 120
cshapeY = 80
conf_level=0.3
max_angle = pi / 4.0
detect = 0
num_reqs = 10
v_width = 16.
v_length = 24.
err_marrgin = 5
actions = [pygame.K_UP,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_DOWN]
live_sticher_limit=10

def display_img():
	c=0;
	if not args.multi:
		test = subprocess.check_output(fetch_last_img, shell=True)
		img_name = args.st_dir + "/" + test.decode("utf-8").strip()
	else:
		####### get stitched image here
		#print "using multi. using live_sticher"
		img_name = live_stitcher.live_stitcher(args.st_dir)
		while (img_name is None and c<live_sticher_limit):
			c=c+1;
		#	print "using.livesticher counter:%d"%(c)
			img_name = live_stitcher.live_stitcher(args.st_dir)
		######
	if (img_name is None):
		print "img_name is none"
		return
	#print "load image from disk"
#	pil_img = Image.open(img_name)
#	if type(pil_img) != type(None):
#		# pil_img = pil_img.crop((0, oshapeY // 3, oshapeX, oshapeY))
#		pil_img = ImageOps.autocontrast(pil_img, 10)
#		cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
#		print "destroy prev windows. show new image."
#		cv2.destroyAllWindows()
#		cv2.imshow(img_name, cv_img)
#		cv2.waitKey(1)
#		print "return image name"
#		return img_name
	img=pygame.image.load(img_name) 
	if img:
		img = pygame.transform.scale(img,(w,h))
		screen.blit(img,(0,0))
		pygame.display.flip()
		return
	print ("Error: couldn't get an image")
	return ""

def record_data(img_name, act_i):
	global correct
	if act_i < 6:
		# if correct:
		# 	sa_lst.pop()
		# 	correct = False
		ts = time.time()
		st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
		new_name = st + "_" + img_name.split("/")[-1]
		print(img_name, new_name)
		sa_lst.append([new_name, act_i])
		shutil.copy(img_name, img_dir + new_name)
	#disregard below. we do record reverse now.
	# Erase data on reverse commands
	#elif act_i < 6:
	#	# correct = True
	#	sa_lst.pop()

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

def manual_drive(img_name,keys):
	for act_i in range(len(actions)):
		tmp=actions[act_i]
		if keys[tmp]:
			print "key pressed %d"%(tmp)
			res = send_control(act_i, img_name)
			break

def reverse_motion():
	last_command = sa_lst[-1][-1]
	block_lst[-1].append(last_command)
	inv_command = last_command + 3
	send_control(inv_command, img_name)

def emergency_reverse():
	print("Sending command %s" % links[3])
	r = urllib2.urlopen(clinks[3], timeout=2)

def auto_drive(img_name):

	res = 1 if not detect else check_position()
	if res == 1:
		# If we are in the right track
		if len(sa_lst) == len(block_lst):
			block_lst.append([])
		md_img, _ = process_image(img_name, None, False)
		pred_act = model.predict(np.array([md_img]))[0]
		print("Lft: %.2f | Fwd: %.2f | Rght: %.2f | Rev: %.2f" % (pred_act[1], pred_act[0], pred_act[2], pred_act[3]))
		act_i = np.argmax(pred_act)
		if (pred_act[act_i]<conf_level):
			emergency_reverse()
		else:
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
	img_name = ""
	drive = False
	keys=[]
	print("before thread")
	while True:
		print "new cycle"
		ct = time.time()
		#print "timestamp :%s"%(ct)
		if (ct - ot) * 1000 > exp_time + delta_time:
			drive = True
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE] or keys[pygame.K_q] or pygame.event.peek(pygame.QUIT):
			print "exit pressed"
			return
		if drive and not auto :
			print "drive"
			drive = False
			manual_drive(img_name,keys)
			ot = ct
		if keys[pygame.K_a]:
			auto = True
			print("Autopilot mode on!")
		if keys[pygame.K_s]:
			auto = False
			print("Autopilot disengaged")
		keys=[]
		pygame.event.pump()
		print "calling display_img()"		
		img_name = display_img()

		# If drive window is open and currently autopilot mode is on
		if auto and drive and img_name:
			print "calling model prediction"	
			drive = False
			pred_act, act_i = auto_drive(img_name)
			ot = ct

if __name__ == '__main__':
	pygame.init()
	size=(w,h)
	screen = pygame.display.set_mode(size) 
	c = pygame.time.Clock() # create a clock object for timing
	
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
		default=250
	)
	
	parser.add_argument(
		'-multi',
		type=int,
		help="Turn multi-cam function on - 1/ off - 0. Default:0",
		default=1
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

	links = ['/fwd', '/fwd/lf', '/fwd/rt', '/rev', '/rev/lf', '/rev/rt', '/exp' + str(args.exp_time)]
	clinks = [args.url + el for el in links]
	sa_lst = []
	block_lst = []
	correct = False
	# Set expiration time for commands
	print "let's check if we have respond from the car"
	exp_time = args.exp_time
	if send_control(6, ""):
		print("Exiting")
		pygame.quit()
		exit(0)
	
	print "fully initialized. ready to drive."
	drive(auto)
	print "done driving"
	if train:
		df = pd.DataFrame(sa_lst, columns=["img_name", "command"])
		df.to_csv(data_dir + args.train + '_log.csv', index=False)
	pygame.quit()
