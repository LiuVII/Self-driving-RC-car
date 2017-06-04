import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick labeling")
    parser.add_argument(
        "set",
        type=str,
        help="Name of set to relabel"
    )
    parser.add_argument(
        "value",
        type=int,
        help="Value to be assigned to all of the images"
    )
    args = parser.parse_args()

    data_dir = "./data_sets"
    csv_dir = "./model_data"

    if not os.path.exists(data_dir+"/"+args.set):
        print "No such image set exists"
        exit(1)

    img_path = "%s/%s/data" % (data_dir,args.set)

    # if not os.path.exists(img_path):
    #     print "Image set is empty"
    #     exit(1)

    print
    print "Stitching images..."
    command = "python stitching.py %s" % args.set
    subprocess.check_output(command, shell=True)

    print
    print "Creating csv..."
    data_name = "%s/%s_log.csv" % (csv_dir, args.set)
    with open(data_name, 'w') as csv_file:
        csv_file.write("img_name,command\n")
        for img in os.listdir(img_path):
            output = "%s,%d\n" % (img,args.value)
            csv_file.write(output)

    print
    print "Timestamping images..."
    command = "python manage_data.py %s" % args.set
    subprocess.check_output(command, shell=True)
