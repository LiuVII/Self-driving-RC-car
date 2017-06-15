import os, time
import argparse
import re
import pandas as pd
from datetime import datetime
import shutil
import csv
from collections import deque

def check_parameters():
    if not os.path.exists(data_set_dir+args.record_set+"_log.csv"):
        print "Corresponding log.csv file for %s does not exists" % \
            (args.record_set)
        exit(1)
    elif not os.path.exists(image_set_dir+args.record_set):
        print "%s data set does not exist" % (args.record_set)
        exit(1)

    if not os.path.exists(stream_dir+args.record_stream):
        print "%s stream path does not exist" % (args.record_set)
        exit(1)
    if os.path.exists(data_set_dir+args.output_set+"_log.csv"):
        print "%s output path already exists" % (args.output_set)
        exit(1)

def get_ctime(file_name, path):
    tmp = path+file_name
    ts = os.path.getctime(tmp)
    st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
    stamped_name = st + "_" + file_name

    return stamped_name
    
def process_data():
    in_csv_file = data_set_dir+args.record_set+"_log.csv"
    left_lst = os.listdir(file_path[0])
    right_lst = os.listdir(file_path[1])

    df = pd.read_csv(in_csv_file, names=['img_left','img_right','command'])

    entries = []
    ind = 2
    st_ind = 1
    end_ind = -1
    ranges = []
    while ind < len(df.index):
        if df['command'].iloc[st_ind] == df['command'].iloc[ind]:
            end_ind = ind
        else:
            if end_ind >= 0:
                ranges.append([st_ind,end_ind])
            else:
                ranges.append([st_ind,st_ind])
            st_ind = ind
            end_ind = -1
        ind += 1
    if (end_ind >= 0):
        ranges.append([st_ind,end_ind])
    else:
        ranges.append([st_ind,st_ind])

    print(ranges)
    for inds in ranges:
        while left_lst and \
            re.search(".*(IMG_[0-9]*\.bmp$)",df['img_left'].iloc[inds[0]]).group(1) != \
            re.search(".*(IMG_[0-9]*\.bmp$)",left_lst[0]).group(1):
            left_lst = left_lst[1:]
        while right_lst and \
            re.search(".*(IMG_[0-9]*\.bmp$)",df['img_right'].iloc[inds[0]]).group(1) != \
            re.search(".*(IMG_[0-9]*\.bmp$)",right_lst[0]).group(1):
            right_lst = right_lst[1:]

        left_stk = []
        while left_lst and \
            re.search(".*(IMG_[0-9]*\.bmp$)",df['img_left'].iloc[inds[1]]).group(1) != \
            re.search(".*(IMG_[0-9]*\.bmp$)",left_lst[0]).group(1):
            left_stk.append(left_lst[0])
            left_lst = left_lst[1:]
        left_stk.append(left_lst[0])
        left_lst = left_lst[1:]

        right_stk = []
        while right_lst and \
            re.search(".*(IMG_[0-9]*\.bmp$)",df['img_right'].iloc[inds[1]]).group(1) != \
            re.search(".*(IMG_[0-9]*\.bmp$)",right_lst[0]).group(1):
            right_stk.append(right_lst[0])
            right_lst = right_lst[1:]
        right_stk.append(right_lst[0])
        right_lst = right_lst[1:]

        while right_stk and left_stk:
            left_tmp = get_ctime(left_stk[0],file_path[0])
            right_tmp = get_ctime(right_stk[0],file_path[1])
            entries.append([left_tmp, right_tmp, df['command'].iloc[inds[0]]])
            shutil.copy(file_path[0]+left_lst[0],output_path[0]+left_tmp)
            shutil.copy(file_path[1]+right_lst[0],output_path[1]+right_tmp)
            left_stk = left_stk[1:]
            right_stk = right_stk[1:]

    print(len(entries), len(df.index))
    out_csv_file = data_set_dir+args.output_set+"_log.csv"
    with open(out_csv_file, 'w') as out_csv:
        writer = csv.writer(out_csv, delimiter=',')
        writer.writerow(['img_left','img_right','command'])
        for entry in entries:
            writer.writerow(entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Creation")
    parser.add_argument(
        "record_set",
        type=str,
        help="Name of recorded data set"
    )
    parser.add_argument(
        "record_stream",
        type=str,
        help="Name of recording stream path"
    )
    parser.add_argument(
        "output_set",
        type=str,
        help="Name of output data set"
    )
    args =parser.parse_args()

    image_set_dir = "./data_sets/"
    data_set_dir = "./model_data/"
    stream_dir = "./stream/"

    check_parameters()
    print "Start processing"
    print

    # create output folder
    os.mkdir(image_set_dir+args.output_set)
    os.mkdir(image_set_dir+args.output_set+"/left")
    os.mkdir(image_set_dir+args.output_set+"/right")

    file_path = [stream_dir+args.record_stream+"/left/",
                stream_dir+args.record_stream+"/right/"]
    output_path = [image_set_dir+args.output_set+"/left/",
                    image_set_dir+args.output_set+"/right/"]

    process_data()