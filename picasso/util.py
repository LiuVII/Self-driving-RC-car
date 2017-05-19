from PIL import Image
from operator import itemgetter
import numpy as np
from keras.applications.imagenet_utils import (decode_predictions,
                                               preprocess_input)

MODEL_DIM = (160, 120, 3)

# def preprocess(targets):
#     image_arrays = []
#     for target in targets:
#         im = target.resize(MODEL_DIM[:2], Image.ANTIALIAS)
#         im = im.convert('RGB')
#         arr = np.array(im).astype('float32')
#         image_arrays.append(arr)

#     all_targets = np.array(image_arrays)
#     return preprocess_input(all_targets)


def preprocess(targets):
    """Turn images into computation inputs
    Converts an iterable of PIL Images into a suitably-sized numpy array which
    can be used as an input to the evaluation portion of the Keras/tensorflow
    graph.
    Args:
        targets (list of Images): a list of PIL Image objects
    Returns:
        array (float32)
    """
    image_arrays = []
    for target in targets:
        im = target.convert('L')
        im = im.resize(MODEL_DIM[:2], Image.ANTIALIAS)
        arr = np.array(im)
        # im = im.convert('RGB')
        # arr = np.array(im).astype('float32')
        image_arrays.append(arr)

    all_targets = np.array(image_arrays)
    return all_targets.reshape(len(all_targets),
                               MODEL_DIM[0],
                               MODEL_DIM[1], 1).astype('float32') / 255


def postprocess(output_arr):
    images = []
    for row in output_arr:
        im_array = row.reshape(MODEL_DIM[:2])
        images.append(im_array)

    return images


# def prob_decode(probability_array, top=3):
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

def prob_decode(probability_array, top=3):
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
                            'name': str(i),
                            'prob': prob})

        entries = sorted(entries,
                         key=itemgetter('prob'),
                         reverse=True)[:top]

        for entry in entries:
            entry['prob'] = '{:.3f}'.format(entry['prob'])
        results.append(entries)

    return results