"""
Based on:
https://github.com/dolaameng/Udacity-SDC_Behavior-Cloning/tree/master/sdc
"""
import argparse
import os
import shutil
from datetime import datetime
from PIL import Image

import base64
from flask import Flask, render_template
from io import BytesIO
from exmp_train import process_image, model
import eventlet
import eventlet.wsgi
import numpy as np
import socketio

sio = socketio.Server()
app = Flask(__name__)
target_speed = 22
shape = (100, 100, 3)
#model = model(True, shape)

@sio.on('telemetry')
def telemetry(sid, data):
    if data:
        # The current image from the center camera of the car
        img_str = data["image"]
        speed = float(data["speed"])

        # Set the throttle.
        throttle = 1.2 - (speed / target_speed)

        # read and process image
        image_bytes = BytesIO(base64.b64decode(img_str))
        image, _ = process_image(image_bytes, None, False)

        # make prediction on steering
        sa = model.predict(np.array([image]))[0][0]

        if args.image_folder != '':
                image_f = Image.open(image_bytes)
                timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
                image_filename = os.path.join(args.image_folder, timestamp)
                image_f.save('{}.jpg'.format(image_filename))

        print(sa, throttle)
        send_control(sa, throttle)
    else:
        # NOTE: DON'T EDIT THIS.
        sio.emit('manual', data={}, skip_sid=True)

@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)
    send_control(0, 0)

def send_control(steering_angle, throttle):
    sio.emit("steer", data={
    'steering_angle': steering_angle.__str__(),
    'throttle': throttle.__str__()
    }, skip_sid=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument(
        'model',
        type=str,
        help='Path to model h5 file. Model should be on the same path.'
    )
    parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        default='',
        help='Path to image folder. This is where the images from the run will be saved.'
    )
    args = parser.parse_args()

    model = model(True, shape, args.model)
    
    if args.image_folder != '':
        print("Creating image folder at {}".format(args.image_folder))
        if not os.path.exists(args.image_folder):
            os.makedirs(args.image_folder)
        else:
            shutil.rmtree(args.image_folder)
            os.makedirs(args.image_folder)
        print("RECORDING THIS RUN ...")
    else:
        print("NOT RECORDING THIS RUN ...")

    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)