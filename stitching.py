import sys
import os
import time
import argparse
import math
from datetime import datetime
import shutil
from PIL import Image

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Data Manager')
    parser.add_argument(
        'set',
        type=str,
        default='',
        help='Name of image set to stitch'
    )

    args = parser.parse_args()

    set_name = args.set
    img_dir = "./data_sets/"
    data_dir = "./model_data/"

    dir_base = img_dir+set_name
    dir_l = dir_base+"/left"
    dir_r = dir_base+"/right"
    dir_out = dir_base+"/data"

    if not os.path.exists(dir_base):
        print "Data set for %s does not exist" % set_name
        exit(1)
    if not os.path.exists(dir_l) or not os.path.exists(dir_r):
        print "Data set does not have 2 cameras..."
        exit(1)
    if os.path.exists(dir_out):
        print "Stitched folder already exists"
        exit(1)

    os.mkdir(dir_out)

    img_counter = 0
    list_l = [os.path.join(dir_l, x) for x in os.listdir(dir_l)]
    list_r = [os.path.join(dir_r, x) for x in os.listdir(dir_r)]

    while list_l and list_r:
        l_time = os.path.getmtime(list_l[0])
        r_time = os.path.getmtime(list_r[0])

        if l_time == r_time:
            img_counter += 1
            out_name = "%s/IMG_%05d.jpg" % (dir_out,img_counter)
            stitch(list_l[0], list_r[0], out_name)
            list_l = list_l[1:]
            list_r = list_r[1:]
            print (l_time, r_time)
        else:
            if l_time < r_time:
                list_l = list_l[1:]
            else:
                list_r = list_r[1:]
