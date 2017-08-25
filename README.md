# Self-driving-RC-car
Self-driving car project inspired by Udacity and Nvidia

# Driving

Drive manually:
```bash
python capture2.py -out_dir stream/my_dir
python drive5.py -st_dir stream/my_dir -multi ...
```

Drive with model:
```bash
python capture2.py -out_dir stream/my_dir
python drive5.py -st_dir stream/my_dir -multi -model models/my_model.h5 ...
```

# Training

Interpolate data:
```bash
python script_multi rec_data rec_data my_data
```

Check for duplicates:
```bash
python img_similiarity_detection_multi.py -cutoff 0.2 data_sets/my_data
```
you may set your own cutoff

Augment image set:
```bash
python img_augment_tmp.py my_data
```

Merge data_sets:
```bash
python manage_data_multi.py -set my_data -out_set to_train old_set
```

Train model on image set:
```bash
python train4.py -multi -batch 50 -epoch 10 to_train 100
```
user should specify batch size, num of training epochs and num training steps
