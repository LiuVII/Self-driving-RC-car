from __future__ import print_function
import pygame
import os, sys, time, shutil
import csv
import argparse
import logging
import numpy as np
from train4 import process_image, model

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')

NUM_CLASSES = 4

oshapeX = 640
oshapeY = 480
#Orignal Multi size
moshapeX = 640 * 2
moshapeY = 480
#Scaled Image size
shapeX = 160
shapeY = 120
#Scaled Multi size
mshapeX = 320
mshapeY = 120

conf_level = .3

actions=['STRAIGHT','LEFT','RIGHT','REVERSE']

def build_parser():
    parser = argparse.ArgumentParser("Date Set Viewer")
    parser.add_argument(
        'data_set',
        type=str,
        help="Name of data set"
    )
    parser.add_argument(
        'model',
        type=str,
        help="model"
    )
    return parser

def wait_key(command):
    global screen
    while True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q] or \
            pygame.event.peek(pygame.QUIT):
            logging.info('\rExiting...')
            return (-1)
        elif keys[pygame.K_UP]:
            logging.debug("\rup pressed")
            return (0)
        elif keys[pygame.K_DOWN]:
            logging.debug("\rdown pressed")
            return (3)
        elif keys[pygame.K_LEFT]:
            logging.debug("\rleft pressed")
            return (1)
        elif keys[pygame.K_RIGHT]:
            logging.debug("\rright pressed")
            return (2)
        elif keys[pygame.K_a]:
            logging.info("\rMOVE BACK <-")
            return (4)
        elif keys[pygame.K_d]:
            logging.info("\rMOVE FORWARD ->")
            return (5)
        elif keys[pygame.K_SPACE]:
            return (command)
        # else:
            # logging.debug("\rIncorrect input")

def display_image(image_path, data_path):

    ot = 0
    print ("display_image")
    left_path = image_path+"/left/"
    right_path = image_path+"/right/"
    entries = None
    attributes = None
    with open(data_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        attributes = next(reader, None)
        entries = list(reader)
        i = 0
        while i < len(entries):
            left_img = entries[i][0]
            right_img = entries[i][1]
            command = int(entries[i][2])
            left_name = left_path+left_img
            right_name = right_path+right_img
            left_img = pygame.image.load(left_path+left_img)
            right_img = pygame.image.load(right_path+right_img)
            if left_img and right_img:
                img_left = pygame.transform.scale(left_img,(oshapeX,oshapeY))
                img_right = pygame.transform.scale(right_img,(oshapeX,oshapeY))
                screen.blit(img_left,(0,0))
                screen.blit(img_right,(oshapeX,0))
                print (left_name, right_name)
                md_img, _ = process_image([left_name,right_name], None, False, True, shape=(shapeY,shapeX))
                pred_act = model.predict(np.array([md_img]))[0]
                pred = "Lft: %.2f | Fwd: %.2f | Rht: %.2f | Rev: %.2f" % \
            (pred_act[1], pred_act[0], pred_act[2], pred_act[3])
                pygame.display.set_caption(actions[command] + " | " + pred)
                pygame.display.flip()
            # print(entries[i])
            act_i = np.argmax(pred_act)
            print (actions[act_i])
            if (pred_act[act_i]<conf_level):
                act_i = 3
            print ("final: ", actions[act_i], actions[command])
            if (act_i == 3 and command == 0) or (act_i == 0 and command == 3):
                press = wait_key(command)
                if press < 0:
                # exiting and go forward with writing csv
                    break
                elif press > 3:
                    if press == 4:
                        if i == 0:
                            logging.warning("Can't do that, at earliest")
                        else:
                            i -= 1
                    else:
                        if i == len(entries):
                            logging.warning("Can't do that, at latest")
                        else:
                            i += 1 
                else:
                    i += 1
                    entries[i][2] = press
                    # print("changed")
                    # print(entries[i])
                ct = time.time()
                while (ct - ot) * 1000 < 100:
                    pygame.event.clear()
                    pygame.event.pump()
                    ct = time.time()
                ot = ct
            else:
                i += 1

    #write file
    # print(entries)
    if entries:
        with open(data_path, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(attributes)
            for row in entries:
                writer.writerow(row)

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    img_path = "./data_sets/%s" % args.data_set
    if not os.path.exists(img_path):
        logging.error("Error: data set doest not exist.")
        exit(1)
    label_path = "./model_data/%s_log.csv" % args.data_set
    if not os.path.exists(label_path):
        logging.error("Error: data set does not have labels.")
        exit(1)

    shape = (mshapeY, mshapeX, 3)
    model = model(True, shape, tr_model=args.model)
    pygame.init()
    size = (moshapeX,oshapeY)
    screen = pygame.display.set_mode(size)
    display_image(img_path, label_path)
    pygame.quit()