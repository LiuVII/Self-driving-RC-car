#!/bin/bash  
nm="arch$(date +%F_%R).zip"
zip -r $nm model_data data_sets st_dir  
gsutil cp $nm gs://42-robocars/
