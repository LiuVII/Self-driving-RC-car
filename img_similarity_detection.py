
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
	path = args.img_dir + "/data/"
	log_file = "model_data/" + args.img_dir.split("/")[-1] + "_log.csv"
	nodup_file  = "model_data/nd_" + args.img_dir.split("/")[-1] + "_log.csv"
	if not os.path.exists(log_file) or not os.path.exists(path):
		print("File %s doesn't exist" % log_file)
		exit(0)
	if not os.path.exists(path):
		print("Path %s doesn't exist" % path)
		exit(0)
	prev_img = None
	prev_name = ""
	rat_lst = []
	res_lst = []
	df = pd.read_csv(log_file, names=['img_name', 'command'])
	ind = 1
	sa_lst = []
	sample_length = len(df)
	count = 0
	for ind in range(sample_length):
		try:
			img_name = df['img_name'].iloc[ind]
			img_path = os.path.join(path, img_name)
			command = df['command'].iloc[ind]
			# print(img_path)
			img = cv2.imread(img_path, 1)
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
				print("Image %s is a duplicate of %s" % (img_name, prev_name))
				count += 1
				continue
			sa_lst.append([img_name, command])
			prev_img = img
			prev_name = img_name
			res_lst.append(ratio)
		except:
			print("Some mistake")
			continue
	if args.cutoff:
		df = pd.DataFrame(sa_lst, columns=["img_name", "command"])
		df.to_csv(nodup_file, index=False)
	
	if args.cutoff:
		print("Duplicates detected: %d" % count)
