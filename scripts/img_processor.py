
import argparse
import os, sys
from PIL import Image
from PIL import ImageOps
from keras.preprocessing.image import img_to_array, load_img

oshapeX = 640
oshapeY = 240
NUM_CLASSES = 3
shapeX = 320
shapeY = 120
cshapeY = 80

def process_image(path, shape=(shapeY, shapeX)):
	"""Process and augment an image."""
	image = load_img(path, target_size=shape)
	image = image.crop((0, shapeY // 3, shapeX, shapeY))
	image = ImageOps.autocontrast(image, 15)
	return image

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Image Modifier')
	parser.add_argument(
		'img_dir',
		type=str,
		help='Name of the training set folder without /data suffix. Default: ""',
		default=''
	)

	args = parser.parse_args()
	if not args.img_dir:
		print("No image folder specified")
		exit(0)
	path = args.img_dir + "/data/"
	out_path = args.img_dir + "/mod_data/"
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	for item in os.listdir(path):
		try:
			img_path = os.path.join(path, item)
			out_img_path = os.path.join(out_path, item)
			mod_img = process_image(img_path)
			mod_img.save(out_img_path)
		except:
			continue