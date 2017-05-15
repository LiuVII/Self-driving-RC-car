import numpy as np
import cv2
import subprocess
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime
import time
from math import sqrt, pi, cos, sin
import pandas as pd


# Data folder name annd path
dir_name = "data/"
outdir = "outdir/"
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


## Init steering params
st_min_val = 0.48
st_mid_val = 1.51
st_max_val = 2.90
st_curr = 0


# Internal params
fps = 60
tries = 0
ind = 0
t0 = 0.0
r = float(height) / 4.0
r_sq = r * r
d = 2 * r
max_angle = pi / 4.0

# Read csv from file into dataframe
df = pd.read_csv("out.csv", names=['img_name', 'datetime', 'steering'])
# sa_lst = [[],[]]
sa_lst = []
sample_length = len(df)

# Set steering boundaries
if min(df['steering']) < st_min_val:
	st_min_val = min(df['steering'])
if max(df['steering']) > st_max_val:
	st_max_val = min(df['steering'])
st_right_rng = st_mid_val - st_min_val
st_left_rng = st_max_val - st_mid_val


while tries < 10 and ind < sample_length:
	# Measure time to keep certain drawing speed
	t1 = time.time()
	if t1 - t0 > 1.0 / fps:
		
		st_curr = float(df['steering'].iloc[ind])
		if st_curr > 0 and st_curr < st_mid_val:
			angle = ((st_curr - st_mid_val) / st_right_rng) * max_angle
		elif st_curr > 0:
			angle = ((st_curr - st_mid_val) / st_left_rng) * max_angle
		else:
			angle = 0
		# img_name = subprocess.check_output("ls " + dir_name + " | tail -n1", shell=True).decode("utf-8").strip()
		# str_num = str(num)
		# img_name = full_path + dir_name + "IMG_" + (5 - len(str_num))*'0' + str_num + ".jpg"
		img_name = full_path + dir_name + df['img_name'].iloc[ind]
		print(img_name)
		
		img = cv2.imread(img_name, 1)
		
		## If image is valid draw and display, else try again and inct tries counter
		if type(img) != type(None):
			tries = 0
			
			## Clear screen
			cv2.destroyAllWindows()
			
			## Change num to CSV oordinate
			x_shift = r * sin(angle)
			y_shift = r * cos(angle)
			cv2.line(img,(int(width / 2 - r), int(height - r)),(width // 2, height),(0,0,255),5)
			cv2.line(img,(int(width / 2 + r), int(height - r)),(width // 2, height),(0,0,255),5)
			cv2.line(img,(int(width / 2 - x_shift), int(height - y_shift)),(width // 2, height),(255,0,0),5)
			# shift = int(sqrt(r_sq - (r - num % d) ** 2))
			# cv2.line(img,(int(width / 2 - r + num % d), int(height - shift)),(width // 2, height),(255,0,0),5)
			
			## Print img_name and angle to STDOUT and save to the list
			print("%s, %.2f" % (df['img_name'].iloc[ind], angle))
			# sa_lst[0].append(df['img_name'].iloc[ind])
			# sa_lst[1].append(angle)
			sa_lst.append([df['img_name'].iloc[ind], angle])
			## Show combined image
			str_ind = str(ind)
			# cv2.imwrite(outdir + "IMG_" + (5 - len(str_ind))*'0' + str_ind + ".jpg", img)
			cv2.imshow(img_name, img)
			if cv2.waitKey(int(100.0 / fps)) & 0xFF == ord('q'):
				break

		else:
			tries += 1
		t0 = t1
		ind += 1
	# tries += 1
if tries == 10:
	print("Error: no feedback from video")
cv2.destroyAllWindows()
df = pd.DataFrame(sa_lst, columns=["img_name", "steering_angle"])
df.to_csv(data_dir + 'driving_log.csv', index=False)