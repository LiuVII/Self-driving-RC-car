from __future__ import print_function
import os, sys, io
from PIL import Image, ImageFont, ImageDraw
import PIL
from keras.preprocessing.image import img_to_array
from train import model
import numpy as np
import datetime

images = []
start = datetime.datetime.now()
model_time = datetime.timedelta()

if len(sys.argv) != 3:
	print("Usage: python occlusion_mask.py image model")
	exit(0)

def classification(image_data):
	# Read in the image_data
	# image_data = tf.gfile.FastGFile(image_path, 'rb').read()
	with tf.Session() as sess:
	    # Feed the image_data as input to the graph and get first prediction
	    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

	    predictions = sess.run(softmax_tensor, \
	             {'DecodeJpeg/contents:0': image_data})

	    # Sort to show labels of first prediction in order of confidence
	    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

#	    for node_id in top_k:
#	        human_string = label_lines[node_id]
#	        score = predictions[0][node_id]
#	        print('%s (score = %.5f)' % (human_string, score))
	    return (top_k, label_lines, predictions[0])

def apply_mask(img, mask_size, step, nums):
	global model_time
	width = 320
	height = 120
	mask = img.copy()
	map0 = Image.new("RGB", (width, height))
	map1 = Image.new("RGB", (width, height))
	map2 = Image.new("RGB", (width, height))
	map3 = Image.new("RGB", (width, height))
	pixels = mask.load()
	pixels0 = map0.load()
	pixels1 = map1.load()
	pixels2 = map2.load()
	pixels3 = map3.load()
	for i in range(mask_size):
		for j in range(mask_size):
			if i < height and j < width:
				pixels[j, i] = (127, 127, 127)
	for i in range(0, height, step):
		for j in range(0, width, step):
			new_img = img.copy()
			pixels = new_img.load()
			for r in range(i - mask_size // 2, i + (mask_size + 1) // 2):
				for c in range(j - mask_size // 2, j + (mask_size + 1) // 2):
					if r >= 0 and r < height and c >= 0 and c < width:
						pixels[c, r] = (127, 127, 127)
			model_start = datetime.datetime.now()
			aimage = img_to_array(new_img)
			aimage = aimage.astype(np.float32) / 255
			aimage = aimage - 0.5
			res = model.predict(np.array([aimage]))[0]
			model_time += datetime.datetime.now() - model_start
			# print(res)
			for r in range(i, min(i + step, height)):
				for c in range(j, min(j + step, width)):
					pixels0[c, r] = (int((1 - res[0]) * 255), 0, int(res[0] * 255))
					pixels1[c, r] = (int((1 - res[1]) * 255), 0, int(res[1] * 255))
					pixels2[c, r] = (int((1 - res[2]) * 255), 0, int(res[2] * 255))
					pixels3[c, r] = (int((1 - res[3]) * 255), 0, int(res[3] * 255))
	draw0 = ImageDraw.Draw(map0)
	draw1 = ImageDraw.Draw(map1)
	draw2 = ImageDraw.Draw(map2)
	draw3 = ImageDraw.Draw(map3)
	draw = ImageDraw.Draw(mask)
	draw0.text((0, 0), "Forward %.2f" % nums[0], (0, 255, 0), font)
	draw1.text((0, 0), "Left %.2f" % nums[1], (0, 255, 0), font)
	draw2.text((0, 0), "Right %.2f" % nums[2], (0, 255, 0), font)
	draw3.text((0, 0), "Reverse %.2f" % nums[3], (0, 255, 0), font)
	draw.text((0, 0), str(mask_size), (0, 255, 0), font)
	final = Image.new("RGB", (width*2, 12 * height))
	img = img.resize((640,240),PIL.Image.ANTIALIAS)
	map0 = map0.resize((640,240),PIL.Image.ANTIALIAS)
	map1 = map1.resize((640,240),PIL.Image.ANTIALIAS)
	map2 = map2.resize((640,240),PIL.Image.ANTIALIAS)
	map3 = map3.resize((640,240),PIL.Image.ANTIALIAS)
	mask = mask.resize((640,240),PIL.Image.ANTIALIAS)

	final.paste(img, (0, 0, 640, 240))
	final.paste(map0, (0, 240, 640, 480))
	final.paste(map1, (0, 480, 640, 720))
	final.paste(map2, (0, 720, 640, 960))
	final.paste(map3, (0, 960, 640, 1200))
	final.paste(mask, (0, 1200, 640, 1440))
	images.append(final)

inp = Image.open(sys.argv[1])

model = model(True, (120, 320, 3), tr_model=sys.argv[2])
inp = inp.resize((320, 120))
font = ImageFont.truetype("/System/Library/Fonts/SFNSText.ttf", 16)

aimage = img_to_array(inp)
aimage = aimage.astype(np.float32) / 255
aimage = aimage - 0.5
res = model.predict(np.array([aimage]))[0]

for i in range(1, 120, 4):
	apply_mask(inp, i, 5, res)
	img = images.pop(0)
	img.save("map"+str(i)+".jpg")
print(datetime.datetime.now() - start)
print(model_time)
