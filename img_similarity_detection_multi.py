
import argparse
import os, sys
from PIL import Image
from PIL import ImageOps
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

oshapeX = 640
oshapeY = 240
NUM_CLASSES = 3
shapeX = 320
shapeY = 120
cshapeY = 80

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Image Modifier')
	parser.add_argument(
		'img_dir',
		type=str,
		help='Name of the training set folder without /data suffix. Default: ""',
		default=''
	)
	parser.add_argument(
		'-cutoff',
		type=float,
		help='Images similiarity threshold, typical value would be 0.1. Default: 0.',
		default=0.
	)

	args = parser.parse_args()
	if not args.img_dir:
		print("No image folder specified")
		exit(0)
	# path = args.img_dir + "/data/"
	path = [args.img_dir + "/left/",
			args.img_dir + "/right/"]
	log_file = "model_data/" + args.img_dir.split("/")[-1] + "_log.csv"
	nodup_file  = "model_data/nd_" + args.img_dir.split("/")[-1] + "_log.csv"
	# if not os.path.exists(log_file) or not os.path.exists(path):
	# 	print("File %s doesn't exist" % log_file)
	# 	exit(0)
	# if not os.path.exists(path):
	# 	print("Path %s doesn't exist" % path)
	# 	exit(0)
	prev_img = None
	prev_name = ""
	rat_lst = []
	res_lst = []
	df = pd.read_csv(log_file, names=['img_left', 'img_right', 'command'], header=0)
	ind = 1
	sa_lst = []
	sample_length = len(df)
	count = 0
	for ind in range(sample_length):
		# try:
		img_name_lf = df['img_left'].iloc[ind]
		img_name_rt = df['img_right'].iloc[ind]
		img_paths = [os.path.join(path[0],img_name_lf),
					os.path.join(path[1], img_name_rt)]
		command = df['command'].iloc[ind]
		print(img_paths)
		img_lf = cv2.imread(img_paths[0], 1)
		img_rt = cv2.imread(img_paths[1], 1)
		# print (img_lf.size, img_rt.size)
		img = np.concatenate((img_lf, img_rt), axis=1)
		# cv2.imshow("img",img)
		# if type(prev_img) != type(None):
			# img_show = np.concatenate((img, prev_img), axis=0)
			# cv2.imshow("prev", prev_img)
		# cv2.waitKey()
		img = img / 255.
		if type(prev_img) != type(None):
			diff = np.fabs(img - prev_img)
			avg = (img + prev_img) / 2.
			ratio = np.sum(diff) / np.sum(avg)
		else:
			ratio = 1.
		rat_lst.append(ratio)
		# Determine visibly the cutoff
		if ratio < args.cutoff:
			# print(img_name)
			# os.remove(args.img_dir+"/left/"+img_name_lf)
			# os.remove(args.img_dir+"/right/"+img_name_rt)
			# print("Image %s is a duplicate of %s" % (str([img_name_lf,img_name_rt]), str(prev_name)))
			count += 1
			continue
		print("Not dupe")
		sa_lst.append([img_name_lf, img_name_rt, command])
		prev_img = img
		prev_name = [img_name_lf, img_name_rt]
		res_lst.append(ratio)
		# except:
		# 	print("Some mistake")
		# 	continue
	if args.cutoff:
		df = pd.DataFrame(sa_lst, columns=["img_left", "img_right", "command"])
		df.to_csv(nodup_file, index=False)
	
	if args.cutoff:
		print("Duplicates detected: %d" % count)
