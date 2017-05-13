""""
With admiration for and inspiration from:
    https://github.com/dolaameng/Udacity-SDC_Behavior-Cloning/
    https://devblogs.nvidia.com/parallelforall/deep-learning-self-driving-cars/
    https://chatbotslife.com/using-augmentation-to-mimic-human-driving-496b569760a9
    https://www.reddit.com/r/MachineLearning/comments/5qbjz7/p_an_autonomous_vehicle_steering_model_in_99/dcyphps/
Accompanies the blog post at https://medium.com/@harvitronix/training-a-deep-learning-model-to-steer-a-car-in-99-lines-of-code-ba94e0456e6a
"""
import csv, random, numpy as np
from keras.models import load_model, Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.preprocessing.image import img_to_array, load_img, flip_axis, random_shift

def model(load, shape, checkpoint=None):
    """Return a model from file or to train on."""
    if load and checkpoint: return load_model(checkpoint)

    conv_layers, dense_layers = [32, 32, 64, 128], [1024, 512]
    
    model = Sequential()
    model.add(Conv2D(32, 3, 3, activation='elu', input_shape=shape))
    model.add(MaxPooling2D())
    for cl in conv_layers:
        model.add(Conv2D(cl, 3, 3, activation='elu'))
        model.add(MaxPooling2D())
    model.add(Flatten())
    for dl in dense_layers:
        model.add(Dense(dl, activation='elu'))
        model.add(Dropout(0.5))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mse', optimizer="adam")
    return model
    
def get_X_y(data_file):
    """Read the log file and turn it into X/y pairs. Add an offset to left images, remove from right images."""
    X, y = [], []
    steering_offset = 0.4
    with open(data_file) as fin:
        reader = csv.reader(fin)
        next(reader, None)
        for _, left_img, right_img, steering_angle, _, _, speed in reader:
            try:
                if float(speed) < 20: continue  # throw away low-speed samples
            except:
                print(speed)
                exit(0)
            X += [left_img.strip(), right_img.strip()]
            y += [float(steering_angle) + steering_offset, float(steering_angle) - steering_offset]
    return X, y

def process_image(path, steering_angle, augment, shape=(100,100)):
    """Process and augment an image."""
    image = load_img(path, target_size=shape)
    
    if augment and random.random() < 0.5:
        image = random_darken(image)  # before numpy'd

    image = img_to_array(image)
        
    if augment:
        image = random_shift(image, 0, 0.2, 0, 1, 2)  # only vertical
        if random.random() < 0.5:
            image = flip_axis(image, 1)
            steering_angle = -steering_angle

    image = (image / 255. - .5).astype(np.float32)
    return image, steering_angle

def random_darken(image):
    """Given an image (from Image.open), randomly darken a part of it."""
    w, h = image.size

    # Make a random box.
    x1, y1 = random.randint(0, w), random.randint(0, h)
    x2, y2 = random.randint(x1, w), random.randint(y1, h)

    # Loop through every pixel of our box (*GASP*) and darken.
    for i in range(x1, x2):
        for j in range(y1, y2):
            new_value = tuple([int(x * 0.5) for x in image.getpixel((i, j))])
            image.putpixel((i, j), new_value)
    return image

def _generator(batch_size, X, y):
    """Generate batches of training data forever."""
    while 1:
        batch_X, batch_y = [], []
        for i in range(batch_size):
            sample_index = random.randint(0, len(X) - 1)
            sa = y[sample_index]
            image, sa = process_image("./data/" + X[sample_index], sa, augment=True)
            batch_X.append(image)
            batch_y.append(sa)
        yield np.array(batch_X), np.array(batch_y)

def train():
    """Load our network and our data, fit the model, save it."""
    net = model(load=False, shape=(100, 100, 3))
    X, y = get_X_y('./data/driving_log.csv')
    #print("X\n", X[:10], "y\n", y[:10])
    #original num samples 20224, epoch 2
    net.fit_generator(_generator(256, X, y), samples_per_epoch=50, nb_epoch=1)
    net.save('checkpoints/short.h5')

if __name__ == '__main__':
    train()