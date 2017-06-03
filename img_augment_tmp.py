import os, re, csv, shutil
import itertools
import argparse
import cv2

oshapeX = 640
oshapeY = 240
shapeX = 320
shapeY = 120

def image_autocontrast(image):
    pass

def image_darken(image):
    pass

def image_brighthen(image):
    pass

def image_equalize(image):
    pass

def image_flip(image):
    return cv2.flip(image)

def process_image(path, name, command, shape=(shapeY, shapeX)):
    """Process and augment image"""

    for ops in op_todo:
        file_prefix = ""
        for op in ops:
            if operations[op] == 'flip':
                command = 0 if


def synthesize_images(set_name):
    """Synthesize data from original images"""

    img_path = "data_sets/%s" % (set_name)
    csv_file = "model_data/%s_log.csv" % (set_name)
    with open(csv_file, 'r') as in_csv:
        reader = csv.reader(in_csv, delimiter=',')
        for entry in reader:
            process_image(img_path, entry[0], entry[2])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Processing")
    parser.add_argument(
        "set_name",
        type=str,
        help="Image folder path"
    )
    args = parser.parse_args()
    if not os.path.exists("data_sets/"+args.set_name):
        print "Image set does not exist"
        exit(1)
    if not os.path.exists("model_data/"+args.set_name+"_log.csv"):
        print "Image set data does not exist"
        exit(1)

    op_list = [
        ('autocont',image_autocontrast),
        ('equalize',image_equalize),
        ('flip',image_flip)
    ]

    for ind in range(len(operations)):
        for item in itertools.combinations(op_list, ind+1):
            op_todo.append(item)

    synthesize_images(args.set_name)
