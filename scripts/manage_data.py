import os
import sys
import time
import argparse
from datetime import datetime
import shutil

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
    	shutil.copytree(src, dst)
    else:
	    for item in os.listdir(src):
	        s = os.path.join(src, item)
	        d = os.path.join(dst, item)
	        shutil.copy(s, d)

def merge_sets(set1, set2, outset):
	set1_img_path = img_dir + set1 + "/" + "data/"
	set1_log = data_dir + set1 + "_log.csv"
	set2_img_path = img_dir + set2 + "/" + "data/"
	set2_log = data_dir + set2 + "_log.csv"
	outset_log = data_dir + outset + "_log.csv"

	copytree(set1_img_path, img_dir + outset + "/data")
	copytree(set2_img_path, img_dir + outset + "/data")
	
	with open(outset_log, "w") as fout:
		with open(set1_log, "r") as fin1:
			header = fin1.readline()
			fout.write(header)
			for line1 in fin1.readlines():
				fout.write(line1)
		with open(set2_log, "r") as fin2:
			header = fin2.readline()
			for line2 in fin2.readlines():
				fout.write(line2)

def shift_set(set_name, shift, outset):
	set_log = data_dir + set_name + "_log.csv"
	outset_log = data_dir + outset + "_log.csv"

	with open(outset_log, "w") as fout:
		with open(set_log, "r") as fin:
			img_names = []
			labels = []
			header = fin.readline()
			fout.write(header)
			for line in fin.readlines():
				data = line.split(",")
				img_names.append(data[0])
				labels.append(",".join(data[1:]))
			num = len(img_names)
			for i in range(max(0, shift), min(num, num + shift)):
				line = img_names[i - shift] + "," + labels[i]
				fout.write(line)


def time_set(set_name):
	set_img_path = img_dir + set_name + "/" + "data/"
	set_log = data_dir + set_name + "_log.csv"

	with open(set_log, "r") as fin:
		img_names = []
		labels = []
		header = fin.readline()
		for line in fin.readlines():
			data = line.split(",")
			if len(data[0]) > 23:
				return
			ts = os.path.getmtime(set_img_path + data[0])
			st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
			img_name = st + "_" + data[0]
			shutil.move(set_img_path + data[0], set_img_path + img_name)
			img_names.append(img_name)
			labels.append(",".join(data[1:]))
	
	with open(set_log, "w") as fout:
		fout.write(header)
		num = len(img_names)
		for i in range(num):
			line = img_names[i] + "," + labels[i]
			fout.write(line)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Data Manager')
	parser.add_argument(
		'set_1',
		type=str,
		default='',
		help='Name of the dataset 1.'
	)
	parser.add_argument(
		'-set',
		type=str,
		default='',
		help='Name of the dataset 2.'
	)
	parser.add_argument(
		'-out_set',
		type=str,
		help='Name of the output dataset',
		default=""
	)
	parser.add_argument(
		'-shift',
		type=int,
		help='Number of label shifts in the dataset. Default: 0',
		default=0
	)
	args = parser.parse_args()

	img_dir = "./data_sets/"
	data_dir = "./model_data/"
	set1_name = args.set_1
	if not os.path.exists(data_dir + set1_name + "_log.csv"):
		print("Corresponding log.csv file for Set 1 was not found")
		exit(1)
	elif not os.path.exists(img_dir + set1_name):
		print("Corresponding img_dir for Set 1 was not found")
		exit(1)
	
	op = ""
	time_set(set1_name)
	if args.set:
		set2_name = args.set.split("/")[-1]
		if not os.path.exists(data_dir + set2_name + "_log.csv"):
			print("Corresponding log.csv file for Set 2 was not found")
			exit(1)
		elif not os.path.exists(img_dir + set2_name):
			print("Corresponding img_dir for Set 1 was not found")
			exit(1)
		op = "m"
		time_set(set2_name)
	elif args.shift:
		op = "s"
	else:
		exit(0)

	if args.out_set:
		out_set = args.out_set
	elif op == "m":
		out_set = set1_name + "-" + set2_name
	else:
		out_set = set1_name + "_s_" + str(args.shift)

	if op == "m":
		merge_sets(set1_name, set2_name, out_set)
	else:
		shift_set(set1_name, args.shift, out_set)
