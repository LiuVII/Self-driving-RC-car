#!/bin/sh

# add_dir.sh <img_dir> <value>

if [ -d "data_sets/$1" ]; then
  if [ ! -e "model_data/$1_log.csv" ]; then
    touch model_data/$1_log.csv
  fi
  ls ./data_sets/$1/data > model_data/$1_log.csv
  python manage_data.py $1
  sed "s/\$/,$2/" model_data/$1_log.csv > model_data/n_$1_log.csv
  cat model_data/n_$1_log.csv > tmp
  echo "img_name,command" > model_data/n_$1_log.csv
  cat tmp >> model_data/n_$1_log.csv
  rm tmp
fi
