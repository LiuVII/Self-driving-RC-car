""""
With admiration for and inspiration from:
    https://github.com/dolaameng/Udacity-SDC_Behavior-Cloning/
    https://devblogs.nvidia.com/parallelforall/deep-learning-self-driving-cars/
    https://chatbotslife.com/using-augmentation-to-mimic-human-driving-496b569760a9
    https://www.reddit.com/r/MachineLearning/comments/5qbjz7/p_an_autonomous_vehicle_steering_model_in_99/dcyphps/
    https://medium.com/@harvitronix/training-a-deep-learning-model-to-steer-a-car-in-99-lines-of-code-ba94e0456e6a
"""
import os
import csv, random, numpy as np, re
import argparse
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.preprocessing.image import img_to_array, load_img, flip_axis, random_shift
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from PIL import Image
import PIL
from PIL import ImageOps
from skimage.exposure import equalize_adapthist

oshapeX = 640
oshapeY = 240
NUM_CLASSES = 4
shapeX = 320
shapeY = 120
cshapeY = 120

def model(load, shape, tr_model=None):
    """Return a model from file or to train on."""
    if load and tr_model: return load_model(tr_model)

    # conv5x5_l, conv3x3_l, dense_layers = [16, 24], [36, 48], [512, 128, 16]
    conv3x3_l, dense_layers = [24, 32, 40, 48], [512, 64, 16]

    model = Sequential()
    model.add(Conv2D(16, (5, 5), activation='elu', input_shape=shape))
    model.add(MaxPooling2D())
    for i in range(len(conv3x3_l)):
        model.add(Conv2D(conv3x3_l[i], (3, 3), activation='elu'))
        if i < len(conv3x3_l) - 1:
            model.add(MaxPooling2D())
    model.add(Flatten())
    for dl in dense_layers:
        model.add(Dense(dl, activation='elu'))
        model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])
    return model

def get_X_y(data_file):
    """Read the log file and turn it into X/y pairs. Add an offset to left images, remove from right images."""
    X, y = [], []
    with open(data_file) as fin:
        reader = csv.reader(fin)
        test = next(reader, None)
        if args.multi:
            if len(test) != 3:
                print("CSV doesn't match for multipel cameras")
                exit(1)
            for img_l, img_r, command in reader:
                X.append([img_l.strip(),img_r.strip()])
                y.append(int(command))
        else:
            for img, command in reader:
                X.append(img.strip())
                y.append(int(command))
    return X, to_categorical(y, num_classes=NUM_CLASSES)

def process_image(file_names, command, augment, multi, shape=(shapeY, shapeX)):
    """Process and augment an image."""
    if multi:
        image_l = load_img(file_names[0], target_size=shape)
        image_r = load_img(file_names[1], target_size=shape)
        images = [image_l, image_r]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
          image.paste(im, (x_offset,0))
          x_offset += im.size[0]
    else:
        image = load_img(file_names[0], target_size=shape)
        #should do some equalizaiton here
    aimage = img_to_array(image)
    aimage = aimage.astype(np.float32) / 255.
    aimage = aimage - 0.5
    return aimage, command

def _generator(batch_size, classes, X, y, augment):
    """Generate batches of training data forever."""
    while 1:
        batch_X, batch_y = [], []
        for i in range(batch_size):
            # random.seed(random.randint(0, 9001))
            class_i = random.randint(0, NUM_CLASSES - 1)
            # sample_index = random.randint(0, len(classes[class_i]) - 1)
            sample_index = random.choice(classes[class_i])
            command = y[sample_index]
            if args.multi:
                file_names = [img_dir_l + X[sample_index][0],
                            img_dir_r + X[sample_index][1]]
                shape=(shapeY,shapeX/2)
            else:
                file_names = [img_dir + X[sample_index]]
                shape=(shapeY,shapeX/2)
            image, command = process_image(file_names, command, augment=augment, multi=args.multi, shape=shape)
            batch_X.append(image)
            batch_y.append(command)
        yield np.array(batch_X), np.array(batch_y)

def train(model_name, val_split, epoch_num, step_num):
    """Load our network and our data, fit the model, save it."""
    if model_name:
        net = model(load=True, shape=(cshapeY, shapeX, 3), tr_model=model_name)
    else:
        net = model(load=False, shape=(cshapeY, shapeX, 3))
    net.summary()
    X, y = get_X_y(data_dir + args.img_dir + '_log.csv')

    # print("X\n", X[:10], "y\n", y[:10])
    Xtr, Xval, ytr, yval = train_test_split(X, y, test_size=val_split, random_state=random.randint(0, 100))
    tr_classes = [[] for _ in range(NUM_CLASSES)]
    for i in range(len(ytr)):
        for j in range(NUM_CLASSES):
            if ytr[i][j]:
                tr_classes[j].append(i)
    val_classes = [[] for _ in range(NUM_CLASSES)]
    for i in range(len(yval)):
        for j in range(NUM_CLASSES):
            if yval[i][j]:
                val_classes[j].append(i)
    net.fit_generator(_generator(batch_size, tr_classes, Xtr, ytr, True),\
        validation_data=_generator(batch_size, val_classes, Xval, yval, False),\
        validation_steps=max(len(Xval) // batch_size, 1), steps_per_epoch=1, epochs=1)
    net.fit_generator(_generator(batch_size, tr_classes, Xtr, ytr, True), \
        validation_data=_generator(batch_size, val_classes, Xval, yval, False),\
        validation_steps=max(len(Xval) // batch_size, 1), steps_per_epoch=step_num, epochs=epoch_num)
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)
    net.save(model_dir + args.img_dir + "_" + str(step_num) + "-"  + str(epoch_num) + "_" + str(batch_size) + "_" \
        + str(shapeX) + "x" + str(shapeY) + '.h5')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trainer')
    parser.add_argument(
        'img_dir',
        type=str,
        help='Name of the training set folder. Default: ts_0',
        default="ts_0"
    )
    parser.add_argument(
        'steps',
        type=int,
        help='Training steps. Default: 200',
        default=200
    )
    parser.add_argument(
        '-batch',
        type=int,
        help='Batch size. Default: 64',
        default=64
    )
    parser.add_argument(
        '-model',
        type=str,
        default='',
        help='Path to model h5 file. Model should be on the same path.'
    )
    parser.add_argument(
        '-valid',
        type=float,
        default=0.15,
        help='Validation fraction of data. Default: 0.15'
    )
    parser.add_argument(
        '-epoch',
        type=int,
        default=1,
        help='Number of training epochs. Default: 1'
    )
    parser.add_argument(
        '-multi',
        action='store_true',
        default=False,
    )

    args = parser.parse_args()

    batch_size = args.batch
    data_dir = "./model_data/"
    pos = args.img_dir.find("_s_")
    if pos > 0:
        img_dir = "./data_sets/" + args.img_dir[:pos] + "/data/"
        if args.multi:
            img_dir_l = "./data_sets/" + args.img_dir + "/left/"
            img_dir_r = "./data_sets/" +  args.img_dir + "/right/"
    else:
        img_dir = "./data_sets/" + args.img_dir + "/data/"
        if args.multi:
            img_dir_l = "./data_sets/" + args.img_dir + "/left/"
            img_dir_r = "./data_sets/" +  args.img_dir + "/right/"
    model_dir = "./models/"
    train(args.model, args.valid, args.epoch, args.steps)
