import numpy as np
import cv2
import subprocess
import os
import sys
import matplotlib.pyplot as plt

tries = 0
dir_name = "data"
full_path = os.path.dirname(os.path.realpath(sys.argv[0]))
while tries < 10:
	img_name = subprocess.check_output("ls " + dir_name + " | tail -n1", shell=True).decode("utf-8").strip()
	img_name = full_path + "/"  + dir_name + "/" + img_name
	print(img_name)
	img = cv2.imread(img_name, 1)
	# img = plt.imread(img_name, 0)
	# plt.show()
	# if 1:
	# print(type(img))
	if type(img) != type(None):
		# print(img)
		# tries = 0
		cv2.destroyAllWindows()
		# plt.imshow(img)
		# plt.xticks([]), plt.yticks([])
		# plt.show()
		cv2.imshow(img_name, img)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	else:
		tries += 1
	# tries += 1
if tries == 10:
	print("Error: no feedback from video")
cv2.destroyAllWindows()