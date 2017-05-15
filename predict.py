"""
Based on:
https://github.com/dolaameng/Udacity-SDC_Behavior-Cloning/tree/master/sdc
"""

import argparse
import os
from PIL import Image

from train import process_image, model
import numpy as np
import cv2
import sys
import time
from math import sqrt, pi, cos, sin
import pandas as pd

# sio = socketio.Server()
# app = Flask(__name__)
# target_speed = 22

# Data folder name annd path
dir_name = "data/"
outdir = "findir/"
full_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"
outdir = full_path + outdir
if not os.path.exists(outdir):
	os.mkdir(outdir)
data_dir = "./model_data/"
if not os.path.exists(data_dir):
	os.mkdir(data_dir)

# Image flow params
width = 320
height = 240
shape = (100, 100, 3)

# ## Init steering params
# st_min_val = 0.48
# st_mid_val = 1.51
# st_max_val = 2.90
# st_curr = 0

# Internal params
fps = 10
tries = 0
ind = 1
t0 = 0.0
r = float(height) / 4.0
r_sq = r * r
d = 2 * r
max_angle = pi / 4.0

parser = argparse.ArgumentParser(description='Remote Driving')
parser.add_argument(
    'model',
    type=str,
    help='Path to model h5 file. Model should be on the same path.'
)
# parser.add_argument(
#     'image_folder',
#     type=str,
#     nargs='?',
#     default='',
#     help='Path to image folder. This is where the images from the run will be saved.'
# )
args = parser.parse_args()

model = model(True, shape, args.model)

# if args.image_folder != '':
#     print("Creating image folder at {}".format(args.image_folder))
#     if not os.path.exists(args.image_folder):
#         os.makedirs(args.image_folder)
#     else:
#         shutil.rmtree(args.image_folder)
#         os.makedirs(args.image_folder)
#     print("RECORDING THIS RUN ...")
# else:
#     print("NOT RECORDING THIS RUN ...")

# Read csv from file into dataframe
df = pd.read_csv(data_dir + "driving_log.csv", names=['img_name', 'steering'])
# sa_lst = [[],[]]
sa_lst = []
sample_length = len(df)

while tries < 10 and ind < sample_length:
	# Measure time to keep certain drawing speed
	t1 = time.time()
	if t1 - t0 > 1.0 / fps:
		
		angle = float(df['steering'].iloc[ind])
		img_name = full_path + dir_name + df['img_name'].iloc[ind]
		img = cv2.imread(img_name, 1)

		## If image is valid draw and display, else try again and inct tries counter
		if type(img) != type(None):
			tries = 0
			
			md_img, _ = process_image(img_name, None, False)
			pred_angle = model.predict(np.array([md_img]))[0][0]
			if pred_angle > max_angle:
				pred_angle = max_angle
			elif pred_angle < -max_angle:
				pred_angle = -max_angle

			## Clear screen
			cv2.destroyAllWindows()
			
			## Change num to CSV oordinate
			x_shift = r * sin(angle)
			y_shift = r * cos(angle)
			cv2.line(img,(int(width / 2 - r), int(height - r)),(width // 2, height),(0,0,255),5)
			cv2.line(img,(int(width / 2 + r), int(height - r)),(width // 2, height),(0,0,255),5)
			cv2.line(img,(int(width / 2 - x_shift), int(height - y_shift)),(width // 2, height),(255,0,0),5)
			
			## Draw prediction line
			x_shift = 1.2 * r * sin(pred_angle)
			y_shift = 1.2 * r * cos(pred_angle)
			cv2.line(img,(int(width / 2 - x_shift), int(height - y_shift)),(width // 2, height),(0,255,0),3)

			## Show combined image
			str_ind = str(ind)
			cv2.imwrite(outdir + "IMG_" + (5 - len(str_ind))*'0' + str_ind + ".jpg", img)
			cv2.imshow(img_name, img)
			if cv2.waitKey(int(100.0 / fps)) & 0xFF == ord('q'):
				break

		else:
			tries += 1
		t0 = t1
		ind += 1
if tries == 10:
	print("Error: failed to load images")
cv2.destroyAllWindows()