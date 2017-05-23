

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


img = load_img(path)
img_ac = PIL.ImageOps.autocontrast(img, cutoff)
img_eq = PIL.ImageOps.equalize(img)
n_img = combine_img([img, img_ac, img_eq])
n_img.show(title="org | ac " + sys.argv[2] + " | equ")



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
