from keras.applications.imagenet_utils import (decode_predictions,
                                               preprocess_input)
import keras.applications.imagenet_utils
from keras.preprocessing.image import img_to_array, load_img
from PIL import Image
import numpy as np
from operator import itemgetter
from PIL import ImageOps

oshapeX = 640
oshapeY = 240
NUM_CLASSES = 3
shapeX = 320
shapeY = 120
cshapeY = 80
MODEL_SHAPE = (cshapeY, shapeX, 3)
actions = ['F', 'L', 'R']

def process_image(image):
    """Process and augment an image."""
    aimage = img_to_array(image)
    aimage = aimage.astype(np.float32) / 255.
    aimage = aimage - 0.5
    return aimage

def preprocess(targets):
    image_arrays = []
    for target in targets:
        # print(target, target.size)
        im = target.resize((cshapeY, shapeX), Image.ANTIALIAS)
        arr = process_image(im)
        # im = im.convert('RGB')
        # arr = np.array(im).astype('float32')
        # print(arr)
        print(arr.shape)
        image_arrays.append(arr)

    all_targets = np.array(image_arrays)
    # print(all_targets.shape)
    # print(all_targets)
    # return preprocess_input(all_targets)
    return all_targets.reshape(len(all_targets),
                               MODEL_SHAPE[0],
                               MODEL_SHAPE[1], MODEL_SHAPE[2]).astype('float32')


def postprocess(output_arr):
    images = []
    for row in output_arr:
        # print(im_array, im_array.shape)
        im_array = row.reshape(MODEL_SHAPE[:2])
        images.append(im_array)

    return images


# def prob_decode(probability_array, top=5):
#     r = decode_predictions(probability_array, top=top)
#     results = [
#         [{'code': entry[0],
#           'name': entry[1],
#           'prob': '{:.3f}'.format(entry[2])}
#          for entry in row]
#         for row in r
#     ]
#     classes = keras.applications.imagenet_utils.CLASS_INDEX
#     class_keys = list(classes.keys())
#     class_values = list(classes.values())

#     for result in results:
#         for entry in result:
#             entry.update(
#                     {'index':
#                      int(
#                          class_keys[class_values.index([entry['code'],
#                                                         entry['name']])]
#                      )}
#             )
#     return results
def prob_decode(probability_array, top=5):
    """Provide class information from output probabilities

    Gives the visualization additional context for the computed class
    probabilities.

    Args:
        probability_array (array): class probabilities
        top (int): number of class entries to return. Useful for limiting
            output in models with many classes. Defaults to 5.

    Returns:
        result list of  dict in the format [{'index': class_index, 'name':
            class_name, 'prob': class_probability}, ...]

    """
    results = []
    for row in probability_array:
        entries = []
        for i, prob in enumerate(row):
            entries.append({'index': i,
                            'name': actions[i],
                            'prob': prob})

        entries = sorted(entries,
                         key=itemgetter('prob'),
                         reverse=True)[:top]

        for entry in entries:
            entry['prob'] = '{:.3f}'.format(entry['prob'])
        results.append(entries)

    return results
