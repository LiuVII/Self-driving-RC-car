import sys
import os
import subprocess
import time
import cv2
import numpy as np
from PIL import Image
from PIL import ImageOps

last_left = None
last_right = None
img_counter = 0

def stitch(img_l, img_r, output_name):

    images = map(Image.open, [img_l, img_r])
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    # new_im.show()
    new_im.save(output_name)

def check_valid(out_name):
    img = Image.open(out_name)

    try:
        img.load()
        return True
    except:
        return False

# if __name__ == "__main__":
def live_stitcher(img_dir):
    global last_left, last_right, img_counter
    # img_dir = "./st_dir"
    left = img_dir + "/left"
    right = img_dir + "/right"
    out_dir = img_dir + "/data"

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    fetch_left = "ls " + left + " | tail -n1"
    fetch_right = "ls " + right + " | tail -n1"

    img_left = subprocess.check_output(fetch_left, shell=True)
    img_right = subprocess.check_output(fetch_right, shell=True)

    img_left = os.path.join(left, img_left).strip()
    img_right = os.path.join(right, img_right).strip()

    # if file a file has been used before
    # return None as to not recreate stitched image
    if last_left == img_left or last_right == img_right:
        last_left = img_left
        last_right = img_right
        # print "old file(s) seen"
        return None

    img_counter += 1
    out_name = "%s/IMG_%05d.jpg" % (out_dir, img_counter)
    # print(img_left, img_right, out_name)
    stitch(img_left, img_right, out_name)
    last_left = img_left
    last_right = img_right
    while not check_valid(out_name):
        continue
    return out_name
