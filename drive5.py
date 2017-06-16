from __future__ import print_function
import pygame
import os, sys, time, shutil
from datetime import datetime
import select
import argparse
import urllib2
import subprocess
#import cv2
import numpy as np, pandas as pd
from PIL import ImageOps
from PIL import Image
from train4 import process_image, model
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

NUM_CLASSES = 4
# delta_time = -200
delta_time = 200

#Original Image size
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

conf_level=0.3
# num_reqs = 10
# v_width = 16.
# v_length = 24.
# err_marrgin = 5

actions = [pygame.K_UP,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_DOWN]

def init_sound():
    sounds = {}
    sounds['start'] = pygame.mixer.Sound('assets/sound/start_car.wav')
    sounds['vroom'] = pygame.mixer.Sound('assets/sound/vroom_car.wav')
    sounds['drive'] = pygame.mixer.Sound('assets/sound/drive_car.wav')
    sounds['slow'] = pygame.mixer.Sound('assets/sound/slow_car.wav')
    sounds['idle'] = pygame.mixer.Sound('assets/sound/idle_car.wav')
    return sounds

def verify_args():
    var = {}
    # verify command line arguments
    if os.path.exists(args.st_dir):
        fetch_last_img = "ls " + args.st_dir + " | tail -n1"
        var['fetch_last_img'] = fetch_last_img
    else:
        logging.error("Error: streaming directory %s does not exist" % args.st_dir)
        exit(1)

    if args.wheel:
        delta_time = -100

    if args.multi:
        dir_left = args.st_dir + "/left"
        dir_right = args.st_dir + "/right"
        var['dir_left'] = dir_left
        var['dir_right'] = dir_right
        if os.path.exists(dir_left) and os.path.exists(dir_right):
            fetch_last_left = "ls " + dir_left + " | tail -n1"
            fetch_last_right = "ls " + dir_right + " | tail -n1"
            var['fetch_last_left'] = fetch_last_left
            var['fetch_last_right'] = fetch_last_right
        else:
            logging.error("Error: streaming directory %s is not compatible\
                for mulit-cam" % args.st_dir)
            exit(1)
        shape = (mshapeY, mshapeX, 3)
    else:
        shape = (shapeY, shapeX, 3)

    auto = 0
    if args.model:
        ml_model = model(True, shape, tr_model=args.model)
        auto = args.auto
    else:
        ml_model = None
        auto = False

    train = False
    if args.train:
        train = True
        data_dir = "./model_data/"
        var['data_dir'] = data_dir
        if not args.multi:
            img_dir = "./data_sets/" + args.train + "/data/"
            var['img_dir'] = img_dir
        else:
            img_dir_left = "./data_sets/" + args.train + "/left/"
            img_dir_right = "./data_sets/" + args.train + "/right/"
            if not os.path.exists(img_dir_left):
                os.makedirs(img_dir_left)
            if not os.path.exists(img_dir_right):
                os.makedirs(img_dir_right)
            var['img_dir_left'] = img_dir_left
            var['img_dir_right'] = img_dir_right
    return var, ml_model, auto, train

def display_img():
    ret_img = []
    if not args.multi:
        test = subprocess.check_output(var['fetch_last_img'], shell=True)
        ret_img = [test]
        img_name = args.st_dir + "/" + test.decode("utf-8").strip()
        img = pygame.image.load(img_name)
        if img:
            img = pygame.transform.scale(img,(oshapeX,oshapeY))
            screen.blit(img,(0,0))
            pygame.display.flip()
            return ret_img
    else:
        try:
            img_left = subprocess.check_output(var['fetch_last_left'], shell=True)
            img_right = subprocess.check_output(var['fetch_last_right'], shell=True)
            img_left = var['dir_left'] + "/" + img_left.decode("utf-8").strip()
            img_right = var['dir_right'] + "/" + img_right.decode("utf-8").strip()
            ret_img = [img_left, img_right]
            img_left = pygame.image.load(img_left)
            img_right = pygame.image.load(img_right)
            if img_left and img_right:
                img_left = pygame.transform.scale(img_left,(oshapeX,oshapeY))
                img_right = pygame.transform.scale(img_right,(oshapeX,oshapeY))
                screen.blit(img_left,(0,0))
                screen.blit(img_right,(oshapeX,0))
                pygame.display.flip()
                return ret_img
        except:
            pass
    logging.error("error: couldn't get an image")
    return None

def record_data(act_i, img):
    logging.debug("Entering record_data %d %s" % (act_i, str(img)))
    if act_i < 6:
        ts = time.time()
        st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
        logging.debug(img)
        new_names = [st + "_" + img_name.split("/")[-1] for img_name in img]
        logging.debug(new_names)
        sa_append = new_names + [act_i]
        sa_lst.append(sa_append)
        if args.multi:
            # do left
            shutil.copy(img[0], var['img_dir_left']+new_names[0])
            # do right
            shutil.copy(img[1], var['img_dir_right']+new_names[1])
        else:
            shutil.copy(img[0], var['img_dir']+new_names[0])
    logging.debug("Exiting record_data %d %s" % (act_i, str(img)))

def engine(switch):
    print(engine.drive)
    startup = 0
    if engine.drive == -1:
        startup = 1
    if switch != engine.drive:
        engine.drive = switch
        if engine.drive:
            channel.play(sounds['vroom'], 0, 1000)
        else:
            if not startup:
                channel.play(sounds['slow'], 0, 1000)
    if engine.drive:
        channel.queue(sounds['drive'])
    else:
        channel.queue(sounds['idle'])


def send_control(act_i, img):
    global train, threads
    try:
        logging.info("Sending command %s" % links[act_i])
        if not args.teach:
            r = urllib2.urlopen(clinks[act_i], timeout=2)
        if train and act_i < 6:
            t = threading.Thread(target=record_data, args=(act_i,img))
            t.setDaemon(True)
            # threads.append(t)
            t.start()
        return 0
    except:
        logging.error("send_control: Command %s couldn't reach a vehicle" % clinks[act_i])
        return -1


def manual_drive_ext(img,intent):
    for act_i in range(len(actions)):
        tmp = actions[act_i]
        if tmp==intent:
            logging.debug("acting out %d" % tmp)
            res = send_control(act_i, img)
            return

def manual_drive(img, keys, wheel):
    try:
        r = urllib2.urlopen(args.url+wheel, timeout=2)
        if links[0] in wheel or links[3] in wheel:
            engine(1)
    except:
        logging.error("Error: wheel command failed.")
    # for act_i in range(len(links)):
    #     if links[act_i] == wheel:
    #         res = send_control(act_i, img)
    #         return

def reverse_motion():
    last_command = sa_lst[-1][-1]
    logging.info("Sending command %s" % last_command)
    send_control(inv_command, img_name)

def emergency_reverse():
    logging.info("Sending command %s" % links[3])
    try:
        r = urllib2.urlopen(clinks[3], timeout=2)
    except:
        logging.error("emergency_reverse: Command %s couldn't reach a vehicle" % clinks[3])

def auto_drive(img):
    if img:
        md_img, _ = process_image(img, None, False, args.multi, shape=(shapeY,shapeX))
        pred_act = model.predict(np.array([md_img]))[0]
        logging.info("Lft: %.2f | Fwd: %.2f | Rht: %.2f | Rev: %.2f" %
            (pred_act[1], pred_act[0], pred_act[2], pred_act[3]))
        act_i = np.argmax(pred_act)

        if (pred_act[act_i]<conf_level): emergency_reverse()
        else: send_control(act_i, img)
        return pred_act, act_i
    else:
        logging.error("Error: no image for prediction")
        return None, None

def drive(auto):
    intent=0
    ot = 0
    img = None
    drive = False
    logging.debug("before thread")
    while True:
        ct = time.time()
        drive = True if (ct - ot) * 1000 > exp_time + delta_time else drive
        keys = pygame.key.get_pressed()
        for act_i in range(len(actions)):
            tmp = actions[act_i]
            if keys[tmp]:
                logging.debug("Key pressed %d" % tmp)
                intent=tmp
        if args.wheel:
            wheel = subprocess.check_output("humancontrol/wheeltest")
        else:
            wheel = ''
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q] or \
            pygame.event.peek(pygame.QUIT):
            logging.debug("Exit pressed")
            return
        if drive and not auto:
            logging.debug("Drive")
            drive = False
            if not wheel:
                if args.wheel:
                    engine(0)
                manual_drive_ext(img,intent)
                intent=0
            else:
                manual_drive(img,keys, wheel)
            ot = ct
        if keys[pygame.K_a]:
            auto = True
            logging.info("Autopilot mode on!")
        if keys[pygame.K_s]:
            auto = False
            logging.info("Autopilot mode off!")
        keys=[]
        pygame.event.pump()
        img = display_img()
        logging.debug("Calling display_img()")
        logging.debug(img)
        # If drive windows is open and currently autopilot mode is on
        if auto and drive and img:
            logging.debug("Calling model prediction")
            drive = False
            pred_act, act_i = auto_drive(img)
            ot = ct

def build_parser():
    parser = argparse.ArgumentParser(description='Driver')
    parser.add_argument(
        '-model',
        type=str,
        default='',
        help='Path to model h5 file. Model should be on the same path.'
    )
    parser.add_argument(
        '-auto',
        action='store_true',
        default=False,
        help='Autopilot mode on/off. Default: off'
    )
    parser.add_argument(
        '-multi',
        action='store_true',
        default=False,
        help='Set multi cam on/off. Default: off'
    )
    parser.add_argument(
        '-url',
        type=str,
        help='Url for connection. Default: http://192.168.2.3',
        default="http://192.168.2.3"
    )
    parser.add_argument(
        '-st_dir',
        type=str,
        help='Img stream directory. Default: st_dir',
        default="st_dir"
    )
    parser.add_argument(
        '-exp_time',
        type=int,
        help='Command expiration time. Default: 500ms',
        default=250
    )
    parser.add_argument(
        '-speed',
        type=int,
        help='Command motor power. Default: 250',
        default=250
    )
    parser.add_argument(
        '-train',
        type=str,
        help='Name of the training set. Default: none',
        default=""
    )
    parser.add_argument(
        '-teach',
        action='store_true',
        default=False,
        help='Set teach mode on/off if train flag is enabled. Default: off'
    )
    parser.add_argument(
        '-wheel',
        action='store_true',
        default=False,
        help="Set wheel controls on/off. Default: off"
    )
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    var, model, auto, train = verify_args()

    links = ['/fwd', '/fwd/lf', '/fwd/rt', '/rev', '/rev/lf', '/rev/rt', '/exp' + str(args.exp_time) + '/m'+str(args.speed)]
    clinks = [args.url + el for el in links]
    sa_lst = []
    threads = []

    #Car Startup sound
    if args.wheel:
        pygame.mixer.init()
        sounds = init_sound()
        channel = pygame.mixer.Channel(0)
        channel.play(sounds['start'], 0, 4500)
        #pygame.time.wait(4500)
        engine.drive = -1
        engine(0)

    pygame.init()
    #check car response
    exp_time = args.exp_time
    if send_control(6, None):
        logging.info("Exiting")
        pygame.quit()
        exit(0)

    if not args.multi:
        size = (oshapeX,oshapeY)
    else:
        size = (moshapeX, moshapeY)
    screen = pygame.display.set_mode(size)
    logging.info("Fully initialized. Ready to drive")
    drive(auto)
    logging.info("Done driving")
    # for t in threads:
    #     t.join()
    if train:
        if args.multi:
            column = ["img_left", "img_right", "command"]
        else:
            column = ["img_name", "command"]
        df = pd.DataFrame(sa_lst, columns=column)
        df.to_csv(var['data_dir'] + args.train + "_log.csv", index=False)
    pygame.quit()
