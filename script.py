import os, time
import argparse
import re
from datetime import datetime
import shutil, csv
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

def get_time(file_name, path):

    ts = os.path.getmtime(file_path+file_name)
    st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
    stamped_name = st + "_" + file_name

    return stamped_name, file_name

def process_data():
    in_csv_file = data_set_dir+args.record_set+"_log.csv"
    stream_files_lf = os.listdir(stream_dir+args.record_stream+"/left")
    stream_files_rt = os.listdir(stream_dir+args.record_stream+"/right")

    attributes = None
    out_csv_entries = []
    with open(in_csv_file, 'r') as in_csv:
        reader = csv.reader(in_csv)
        attributes = next(reader, None)
        oldest_entry = next(reader, None)
        newest_entry = None
        cnt = 0
        for row in reader:
            if stream_files:
                if oldest_entry[1] == row[1]:
                    # meaning values are still the same
                    newest_entry = row
                else:
                    print "different", oldest_entry, row, newest_entry
                    while stream_files and \
                        re.search(".*(IMG_[0-9]*\.jpg$)", stream_files[0][0]).group(1) != \
                        re.search(".*(IMG_[0-9]*\.jpg$)", oldest_entry[0]).group(1):
                        stream_files.pop(0)
                    if newest_entry:
                        while stream_files and \
                            re.search(".*(IMG_[0-9]*\.jpg$)", stream_files[0][0]).group(1) != \
                            re.search(".*(IMG_[0-9]*\.jpg$)", newest_entry[0]).group(1):
                            out_csv_entries.append([stream_files[0][0], oldest_entry[1]])
                            shutil.move(file_path+stream_files[0][1],
                                output_path+stream_files[0][0])
                            # print(file_path+stream_files[0][1],
                            #     output_path+stream_files[0][0])
                            stream_files.pop(0)
                        out_csv_entries.append(newest_entry)
                        shutil.move(file_path+stream_files[0][1],
                            output_path+stream_files[0][0])
                        stream_files.pop(0)
                    else:
                        out_csv_entries.append(oldest_entry)
                        shutil.move(file_path+stream_files[0][1],
                            output_path+stream_files[0][0])
                        # print(file_path+stream_files[0][1],
                        #     output_path+stream_files[0][0])
                        stream_files.pop(0)
                    while stream_files and \
                        re.search(".*(IMG_[0-9]*\.jpg$)", stream_files[0][0]).group(1) != \
                        re.search(".*(IMG_[0-9]*\.jpg$)", row[0]).group(1):
                        stream_files.pop(0)
                    oldest_entry = row
                    newest_entry = None

    out_csv_file = data_set_dir+args.output_set+"_log.csv"
    with open(out_csv_file, 'w') as out_csv:
        writer = csv.writer(out_csv, delimiter=',')
        writer.writerow(attributes)
        for entry in out_csv_entries:
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
