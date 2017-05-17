import argparse
import csv
import shutil

def get_data(data_file):
    """Read the log file and turn it into X/y pairs. Add an offset to left images, remove from right images."""
    X, y = [], []
    with open(data_file) as fin:
        reader = csv.reader(fin)
        next(reader, None)
        for img, command in reader:
            X.append(img.strip())
            y.append(actions[int(command)])
    return X, y

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trainer')
    parser.add_argument(
        'img_dir',
        type=str,
        help='Name of the training set folder. Default: ts_0',
        default="ts_0"
    )

    args = parser.parse_args()
    data_dir = "./model_data/"
    actions = ["forward", "left", "right"]
    img_dir = "./data_sets/" + args.img_dir + "/" + "data/"
    out_dir = "./classes/"
    X, y = get_data(data_dir + args.img_dir + '_log.csv')
    for i in range(len(X)):
    	shutil.copy(img_dir + X[i], out_dir + y[i])