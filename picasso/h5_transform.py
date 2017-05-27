from keras.models import load_model
import os, sys
import subprocess
import h5py
import json


# try:
file_name = sys.argv[1]
data_dir = "".join(file_name.split("/")[:-1])
data_volume = "./data-volume"
print("File name: %s" % file_name)
model_name = file_name.split("/")[-1].split(".")[0]
f = h5py.File(file_name, 'r')
print("Data dir: %s, Model name: %s" % (data_dir, model_name))
model = load_model(file_name)
model.save_weights(data_volume + "/" + model_name + ".hdf5")
json_name = data_volume + "/" + model_name + ".json"
with open(json_name, 'w') as outfile:
    # outfile.write(model.to_json())
    json.dump(model.to_json(), outfile)
# except:
# 	print("Usage: [model_path]/[model_file].h5 required")
# 	exit(0)