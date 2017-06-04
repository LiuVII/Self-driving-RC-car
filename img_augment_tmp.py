import os, re, csv, time
import itertools
import argparse
import cv2
import numpy as np
from progress_bar import printProgressBar

oshapeX = 640
oshapeY = 240
shapeX = 320
shapeY = 120

reverse = [0,2,1,3]

# def image_autocontrast(image):
#     # img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     # minVal, maxVal, _minLoc, _maxLoc = cv2.minMaxLoc(img_gray) 
#     # input_range = maxVal - minVal
#     # alpha = 255 / input_range
#     # beta = -minVal * alpha
#     # output = alpha * image + beta
#     # print output.shape, output.size, output.dtype
#     # print image.shape, image.size, image.dtype
#     # return alpha * image + beta
#     # return image
#     B = 0.0
#     W = 0.0
#     hist, bins = np.histogram(image.flatten(),256,[0,256])
#     cdf = np.cumsum(hist)
#     cdf_n = cdf * hist.max() / cdf.max()
#     cdf_m = np.ma.masked_less_equal(cdf, B * cdf.max())
#     cdf_m = np.ma.masked_greater_equal(cdf_m, (1.0 - W) * cdf.max())
#     imin = cdf_m.argmin()
#     imax = cdf_m.argmax()
#     tr = np.zeros(256, dtype=np.uint8)
#     tr = np.zeros(256, dtype=np.uint8)
#     for i in range(0, 256):
#         if i < imin: tr[i] = 0
#         elif i > imax: tr[i] = 255
#         else: tr[i] = (i - imin) * 255 / (imax - imin)
#     img_res = tr[image]
#     return img_res    

def adjust_gamma(image, gamma=1.0):
    # img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # img_hsv[:,:,2] += np.uint8(gamma)
    # image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    # return image
    # print image.shape
    invGamma = 1.0/gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image,table)

def image_darken(image):
    return adjust_gamma(image, .5)

def image_brighten(image):
    return adjust_gamma(image, 2)

# def image_equalize(image):
#     img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
#     img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
#     image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
#     return image

def image_flip(image):
    return cv2.flip(image, 1)

def process_image(path, name, command, op_todo, shape=(shapeY, shapeX)):
    """ProcWss and augmXnt imagY"""

    image_path = path+name
    img_orig = cv2.imread(image_path)
    aug_images = []
    
    # darkening
    # tmp_img = img_orig
    # tmp_img = image_darken(tmp_img)
    # cv2.imwrite(filename=path+"darken_"+name,img=tmp_img)
    # aug_images.append(["darken_"+name,command])
    # # brightening
    # tmp_img = img_orig
    # tmp_img = image_brighten(tmp_img)
    # cv2.imwrite(filename=path+"brighten_"+name,img=tmp_img)
    # aug_images.append(["brighten_"+name,command])

    for ops in op_todo:
        new_image = img_orig
        new_command = command
        output_prepend = ""
        for op in ops:
            output_prepend += op[0]+"_"
            new_image = op[1](new_image)
            if op[0] == 'flip':
                new_command = reverse[new_command]
        aug_images.append([output_prepend+name,new_command])
        cv2.imwrite(filename=path+output_prepend+name,img=new_image)
        # # do darkening and brightening
        # tmp_img = new_image
        # tmp_img = image_darken(tmp_img)
        # cv2.imwrite(filename=path+"darken_"+output_prepend+name,img=tmp_img)
        # aug_images.append(["darken_"+output_prepend+name,new_command])
        # tmp_img = new_image
        # tmp_img = image_darken(tmp_img)
        # cv2.imwrite(filename=path+"brighten_"+output_prepend+name,img=tmp_img)
        # aug_images.append(["brighten_"+output_prepend+name,new_command])

    return aug_images

def synthesize_images(set_name, op_list):
    """Synthesize data from original images"""

    op_todo = [
        (op_list[0]),
        (op_list[1]),
        (op_list[2]),
        (op_list[0],op_list[2]),
        (op_list[1],op_list[2]),
    ]
    # for ind in range(len(op_list)):
    #     for item in itertools.combinations(op_list, ind+1):
    #         op_todo.append(item)

    img_path = "data_sets/%s/data/" % (set_name)
    csv_file = "model_data/%s_log.csv" % (set_name)

    with open(csv_file, 'r') as in_csv:
        for line in in_csv:
            if re.search(r"(flip|autocont|equalize|darken|brighten)", line):
                printProgressBar(1, 1)
                return

    print "Processing images..."
    with open(csv_file, 'a+') as io_csv:
        io_csv.seek(0)
        reader = csv.reader(io_csv, delimiter=',')
        attribute = next(reader, None)
        entries = list(reader)
        cnt_total = len(entries)
        cnt_iter = 0
        printProgressBar(cnt_iter, cnt_total)
        for entry in entries:
            cnt_iter += 1
            printProgressBar(cnt_iter, cnt_total)
            try:
                new_entries = process_image(img_path, entry[0], int(entry[1]), op_todo)
                writer = csv.writer(io_csv, delimiter=',')
                for new_entry in new_entries:
                    writer.writerow(new_entry)
            except:
                print "CSV entry error"
            time.sleep(0.1)

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
        # ('autocont',image_autocontrast),
        # ('equalize',image_equalize),
        ('darken',image_darken),
        ('brighten',image_brighten),
        ('flip',image_flip)
    ]

    synthesize_images(args.set_name, op_list)
    print "Data set has been processed"