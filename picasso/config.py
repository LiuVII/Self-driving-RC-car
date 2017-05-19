import os

base_dir = os.path.split(os.path.abspath(__file__))[0]
# print(base_dir)
BACKEND_ML = 'keras'
BACKEND_PREPROCESSOR_NAME = 'util'
BACKEND_PREPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
BACKEND_POSTPROCESSOR_NAME = 'postprocess'
BACKEND_POSTPROCESSOR_PATH = os.path.join(base_dir, 'util.py')
BACKEND_PROB_DECODER_NAME = 'prob_decode'
BACKEND_PROB_DECODER_PATH = os.path.join(base_dir, 'util.py')
DATA_DIR = os.path.join(base_dir, 'data-volume')