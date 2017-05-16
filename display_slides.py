import numpy as np
import cv2
import subprocess
import argparse
import os
import sys
from datetime import datetime
import time
from math import sqrt, pi, cos, sin
import pandas as pd
from PIL import Image

from train import process_image, model

parser = argparse.ArgumentParser(description='Recorder')
parser.add_argument(
	'img_dir',
	type=str,
	default='tt_1',
	help='Name of the training set folder. Default: tt_1'
)
parser.add_argument(
	'--fps',
	type=int,
	default=5,
	help='FPS (Frames per second) setting for the video.'
)
parser.add_argument(
	'-out_dir',
	type=str,
	default='',
	help='Name of the output folder in the out_dir. Default: None'
)
parser.add_argument(
	'-model',
	type=str,
	default='',
	help='Path to model h5 file. Model should be on the same path.'
)


args = parser.parse_args()

# Data folder name annd path
full_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"
img_path = "./data_sets/" + args.img_dir + "/" + "data/"
if args.out_dir == "":
	saving = False
	print("Warning: not recording this run")
else:
	saving = True
	if not os.path.exists("./out_dir/"):
		os.mkdir("./out_dir")
	out_dir = "./out_dir/" + args.out_dir + "/"
	if not os.path.exists(out_dir):
		os.mkdir(out_dir)
data_dir = "./model_data/"
if not os.path.exists(data_dir):
	os.mkdir(data_dir)

# Model params
predict = False
if args.model:
	shape = (100, 100, 3)
	model = model(True, shape, args.model)
	predict = True
	err = 0

# Image flow params
width = 320
height = 240

# Init steering params
st_min_val = 0.48
st_mid_val = 1.51
st_max_val = 2.90
st_curr = 0

# Internal params
tries = 0
t0 = 0.0
r = float(height) / 4.0
r_sq = r * r
d = 2 * r
max_angle = pi / 4.0

# Read csv from file into dataframe
if predict == False:
	df = pd.read_csv("./data_sets/" + args.img_dir + "/" +\
		"out.csv", names=['img_name', 'datetime', 'steering'])
	ind = 0
else:
	df = pd.read_csv(data_dir + args.img_dir +\
		'_log.csv' , names=['img_name', 'datetime', 'steering'])
	ind = 1
sa_lst = []
sample_length = len(df)

# Set steering boundaries
if predict == False:
	if min(df['steering']) < st_min_val:
		st_min_val = min(df['steering'])
	if max(df['steering']) > st_max_val:
		st_max_val = min(df['steering'])
	st_right_rng = st_mid_val - st_min_val
	st_left_rng = st_max_val - st_mid_val


def get_steering(predict):
	if predict == False:
		st_curr = float(df['steering'].iloc[ind])
		if st_curr > 0 and st_curr < st_mid_val:
			angle = ((st_curr - st_mid_val) / st_right_rng) * max_angle
		elif st_curr > 0:
			angle = ((st_curr - st_mid_val) / st_left_rng) * max_angle
		else:
			angle = 0
	else:
		angle = float(df['steering'].iloc[ind])
	return angle

def	draw_on_img():
	## Clear screen
	cv2.destroyAllWindows()
	
	## Draw red limits
	cv2.line(img,(int(width / 2 - r), int(height - r)),(width // 2, height),(0,0,255),5)
	cv2.line(img,(int(width / 2 + r), int(height - r)),(width // 2, height),(0,0,255),5)
	
	## Draw blue label steering line
	x_shift = r * sin(angle)
	y_shift = r * cos(angle)
	cv2.line(img,(int(width / 2 - x_shift), int(height - y_shift)),(width // 2, height),(255,0,0),5)

def draw_predict():
	## Get prediction steering angle
	md_img, _ = process_image(img_name, None, False)
	pred_angle = model.predict(np.array([md_img]))[0][0]
	if pred_angle > max_angle:
		pred_angle = max_angle
	elif pred_angle < -max_angle:
		pred_angle = -max_angle

	## Draw green prediction line
	x_shift = 1.2 * r * sin(pred_angle)
	y_shift = 1.2 * r * cos(pred_angle)
	cv2.line(img,(int(width / 2 - x_shift), int(height - y_shift)),(width // 2, height),(0,255,0),3)
	return pred_angle

while tries < 10 and ind < sample_length:
	# Measure time to keep certain drawing speed
	t1 = time.time()
	if t1 - t0 > 1.0 / args.fps:	
		angle = get_steering(predict)
		img_name = img_path + df['img_name'].iloc[ind]
		img = cv2.imread(img_name, 1)
		
		## If image is valid draw and display, else try again and inct tries counter
		if type(img) != type(None):
			tries = 0
			
			## Draw limits and control label
			draw_on_img()

			if predict:	
				pred_angle = draw_predict()
				err += abs(pred_angle - angle)
			else:
				## Save img_name and angle to the list
				sa_lst.append([df['img_name'].iloc[ind], df['datetime'].iloc[ind], angle])
			
			## Print img_name and angle to STDOUT and save to the list
			print("%s, %s, %.2f" % (df['img_name'].iloc[ind], df['datetime'].iloc[ind], angle))
			
			## Show combined image
			str_ind = str(ind)
			if saving:
				cv2.imwrite(out_dir + "IMG_" + (5 - len(str_ind))*'0' + str_ind + ".jpg", img)
			cv2.imshow(img_name, img)
			if cv2.waitKey(int(100.0 / args.fps)) & 0xFF == ord('q'):
				break
		else:
			tries += 1
		t0 = t1
		ind += 1
if tries == 10:
	print("Error: no feedback from video")

cv2.destroyAllWindows()

# Save img_names and proper steering values to csv file
if predict == False:
	df = pd.DataFrame(sa_lst, columns=["img_name", "datetime", "steering_angle"])
	df.to_csv(data_dir + args.img_dir + '_log.csv', index=False)
else:
	print("Total error: %f" % (err / float(ind)))