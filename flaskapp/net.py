import random
import keras
from keras.layer import Input
from keras.models import Model
from keras.application.resnet50 import preprocess_input, decode_predictions
import os
from PIL import Image
import numpy as np
from tensorflow.compat.v1 import ConfigProto, InteractiveSession

height = 224
width = 224
nh = 224
nw = 224
ncol = 3

visible2 = Input(shape=(nh, nw, ncol))
resnet = keras.applications.resnet_v2.ResNet50V2(
    include_top=True,
    weights="imagenet",
    input_tensor=visible2,
    input_shape=None,
    pooling=None,
    classes=1000,
)


def reed_image_file(files_max_count, dir_name):
    files = os.listdir(dir_name)
    files_count = files_max_count
    if files_max_count > len(files):
        files_count = len(files)
    image_box = [[]] * files_count
    for file_i in range(files_count):
        image_box[file_i] = Image.open(dir_name + "/" + files[file_i])
    return files_count, image_box


def getresult(image_box):
    files_count = len(image_box)
    image_resized = [[]] * files_count
    for i in range(files_count):
        image_resized[i] = np.array(image_box[i].resize((height, width)))
    image_resized = np.array(image_resized)
    out_net = resnet.predict(image_resized)
    decode = decode_predictions(out_net, top=1)
    return decode
