import os
import csv, random, numpy as np
import PIL
import argparse
import shutil
import re
import itertools
from PIL import Image
from PIL import ImageOps
from skimage.exposure import equalize_adapthist
from keras.preprocessing.image import img_to_array, load_img

oshapeX = 640
oshapeY = 240
shapeX = 320
shapeY = 120
cshapeY = 80

operations = ['autocont', 'equalize', 'flip']

def image_autocontrast(image, name, save_path):
    image = ImageOps.autocontrast(image, 15)
    image.save(save_path+"/"+name)

def darken(image, name, save_path):
    image = image.point(lambda x: x*0.5)
    image.save(save_path+"/"+name)

def brigthen(image, name, save_path):
    image = image.point(lambda x: x*2)
    image.save(save_path+"/"+name)

def image_equalize(image, name, save_path):
    image = ImageOps.equalize(image)
    image.save(save_path+"/"+name)

def image_flip(image, name, save_path):
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    image.save(save_path+"/"+name)

def image_crop(image, name, save_path):
    image = image.crop((0, shapeY // 3, shapeX, shapeY))
    image.save(save_path+"/"+name)

def process_image(path, shape=(shapeY, shapeX)):
    """Process and augment an image"""

    func_ops = [image_autocontrast, image_equalize, image_flip]

    set_root = "./data_sets/%s" % (args.img_folder)

    folders = [path]
    for cnt in range(len(operations)):
        for item in itertools.combinations(range(3), cnt+1):
            src_folder = path
            if len(item) > 1:
                for i in range(len(item) - 1):
                    if i:
                        src_folder += "_"+operations[item[i]]
                    else:
                        src_folder = operations[item[i]]
                src_folder = os.path.join(set_root, src_folder)
            dst_folder = ""
            for i in range(len(item)):
                if i:
                    dst_folder += "_"+operations[item[i]]
                else:
                    dst_folder = operations[item[i]]
            dst_folder = os.path.join(set_root, dst_folder)
            folders.append(dst_folder)
            if not os.path.exists(dst_folder):
                os.mkdir(dst_folder)
            if not os.path.exists(src_folder):
                print "src folder %s does not exist" % (src_folder)
                exit(1)
            for f in os.listdir(src_folder):
                if re.search(".*\.jpg$", f):
                    image = load_img(src_folder+"/"+f, target_size=shape)
                    func_ops[item[-1]](image, f, dst_folder)

    for i in range(len(folders)):
        src_folder = folders[i]
        if not i:
            d_dst_folder = set_root+"/darken"
            b_dst_folder = set_root+"/brigthen"
        else:
            d_dst_folder = folders[i]+"_darken"
            b_dst_folder = folders[i]+"_brigthen"
        if not os.path.exists(d_dst_folder):
            os.mkdir(d_dst_folder)
        if not os.path.exists(b_dst_folder):
            os.mkdir(b_dst_folder)
        for f in os.listdir(src_folder):
            if re.search(".*\.jpg$", f):
                image = load_img(src_folder+"/"+f, target_size=shape)
                darken(image, f, d_dst_folder)
                image = load_img(src_folder+"/"+f, target_size=shape)
                brigthen(image, f, b_dst_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="image processing")
    parser.add_argument(
        "img_folder",
        type=str,
        help="Image folder path"
    )

    data_dir = "./data_sets"
    args = parser.parse_args()
    if not os.path.exists(data_dir+"/"+args.img_folder):
        print "No such image set exists"
        exit(1)
    img_path = "%s/%s/data" % (data_dir,args.img_folder)
    process_image(img_path)
