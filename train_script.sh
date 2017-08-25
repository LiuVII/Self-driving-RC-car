#!/bin/sh

#This script assumes you recorded your image data with the following commands:
#python capture2.py -out_dir stream/rec_data
#python drive5.py -multi -st_dir stream/rec_data -train rec_data ...<args>
#drive5.py -h for help with setting other options

python script_multi rec_data rec_data my_data
python img_similarity_detection_multi.py -cutoff 0.2 data_sets/my_data
mv model_data/nd_my_data_log.csv model_data/my_data_log.csv
python img_augment_tmp.py my_data
python manage_data_multi.py -set my_data -out_set to_train old_set
python train4.py -multi -batch 50 -epoch 10 to_train 100
mv to_train old_set
