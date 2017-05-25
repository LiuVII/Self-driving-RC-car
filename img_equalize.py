

import cv2
import numpy as np
from matplotlib import pyplot as plt

import PIL
import PIL.ImageOps
from keras.preprocessing.image import img_to_array, load_img
import os, sys

from skimage.exposure import equalize_adapthist

if len(sys.argv) < 3:
	exit(0)
path = sys.argv[1]
cutoff = int(sys.argv[2])

def combine_img(images):
	widths, heights = zip(*(i.size for i in images))

	total_width = sum(widths)
	max_height = max(heights)

	new_im = PIL.Image.new('RGB', (total_width, max_height))

	x_offset = 0
	for im in images:
	  new_im.paste(im, (x_offset,0))
	  x_offset += im.size[0]

	return new_im

def cEqualizeHist(img):
	img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

	# equalize the histogram of the Y channel
	img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

	# convert the YUV image back to RGB format
	return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

def histogram_equalize(img, clahe=False):
    b, g, r = cv2.split(img)
    red = cv2.equalizeHist(r)
    green = cv2.equalizeHist(g)
    blue = cv2.equalizeHist(b)
    return cv2.merge((blue, green, red))

def clahe_equalize(img):
    b, g, r = cv2.split(img)
    red = clahe.apply(r)
    green = clahe.apply(g)
    blue = clahe.apply(b)
    return cv2.merge((blue, green, red))

def pil_2_cv(img):
	return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4,4))
for item in os.listdir(path):
	if item.find(".jpg") == -1:
		print("was not found")
		continue
	img = load_img(os.path.join(path, item))
	img_ac = PIL.ImageOps.autocontrast(img, cutoff)
	# img_eq = PIL.ImageOps.equalize(img)
	# n_img = combine_img([img, img_ac, img_eq])
	cv_img = pil_2_cv(img)
	cv_img_ac = pil_2_cv(img_ac)
	# cv_img_eq = cEqualizeHist(cv_img)
	cv_cl = clahe_equalize(cv_img)

	cv_img_eq = histogram_equalize(cv_img)
	# img = cv2.equalizeHist(img)
	cv2.destroyAllWindows()
	res = np.hstack((cv_img,cv_img_ac, cv_img_eq, cv_cl))
	width, height, channels = res.shape
	cv2.imshow(item, cv2.resize(res, (height / 3, width / 3)) )
	if cv2.waitKey(0) & 0xFF == ord('q'):
		break
	# n_img.show(title="org | ac " + sys.argv[2] + " | equ")



# img = cv2.imread(path,0)

# hist,bins = np.histogram(img.flatten(),256,[0,256])
 
# cdf = hist.cumsum()
# # cdf_normalized = cdf * hist.max()/ cdf.max()
# cdf_normalized = cdf / float(cdf.max())
# # print(cdf_normalized)

# plt.plot(cdf_normalized, color = 'b')
# # plt.hist(img.flatten(),256,[0,256], color = 'r')
# plt.xlim([0,256])
# plt.ylim([0,1])
# # plt.legend(('cdf','histogram'), loc = 'upper left')
# cv2.imshow("original", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# # plt.show()

# i = 0
# while cdf_normalized[i] <= 1 - float(cutoff) / 100.:
# 	i += 1
# cutt_ind = i - 1
# for i in range(cutt_ind + 1, len(cdf)):
# 	cdf[i] = cdf[cutt_ind]

# cdf_m = np.ma.masked_equal(cdf,0)
# cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
# cdf = np.ma.filled(cdf_m,0).astype('uint8')
# img2 = cdf[img]

# plt.plot(cdf, color = 'b')
# plt.hist(img2.flatten(),256,[0,256], color = 'r')
# plt.xlim([0,256])
# plt.legend(('cdf','histogram'), loc = 'upper left')
# cv2.imshow("normed", img2)
# cv2.waitKey(0)
# # plt.show()
# cv2.destroyAllWindows()

# img = img_to_array(load_img(path)) 
# img = (img / 255.)
# fig, axs = plt.subplots(1, 4)
# axs[0].imshow(img)
# axs[1].imshow(equalize_adapthist(img))
# axs[2].imshow(equalize_adapthist(img, clip_limit=0.02))
# axs[3].imshow(equalize_adapthist(img, clip_limit=0.05))
# plt.show()
