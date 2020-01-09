#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 12:17:38 2018

@author: github.com/GustavZ
"""
import os
import tarfile
from six.moves import urllib
import numpy as np
import tensorflow as tf
import cv2
from skimage import measure

ALPHA = 0.3
MODEL_NAME = 'deeplabv3_mnv2_pascal_train_aug_2018_01_29'
MODEL_PATH = 'models/deeplabv3_mnv2_pascal_train_aug/frozen_inference_graph.pb'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/'
BBOX = False
MINAREA = 500

graph = None
sess = None

# Hardcoded COCO_VOC Labels
LABEL_NAMES = np.asarray([
    '', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tv'])


def create_colormap(seg_map):
    """
    Takes A 2D array storing the segmentation labels.
    Returns A 2D array where each element is the color indexed
    by the corresponding element in the input label to the PASCAL color map.
    """
    colormap = np.zeros((256, 3), dtype=int)
    ind = np.arange(256, dtype=int)
    for shift in reversed(range(8)):
        for channel in range(3):
            colormap[:, channel] |= ((ind >> channel) & 1) << shift
        ind >>= 3
    return colormap[seg_map]


# Download Model from TF-deeplab's Model Zoo
def download_model():
    model_file = MODEL_NAME + '.tar.gz'
    if not os.path.isfile(MODEL_PATH):
        print('> Model not found. Downloading it now.')
        opener = urllib.request.URLopener()
        opener.retrieve(DOWNLOAD_BASE + model_file, model_file)
        tar_file = tarfile.open(model_file)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd() + '/models/')
        os.remove(os.getcwd() + '/' + model_file)
    else:
        print('> Model found. Proceed.')


# Visualize Text on OpenCV Image
def vis_text(image, string, pos):
    cv2.putText(image, string, (pos),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (77, 255, 9), 2)


# Load frozen Model
def load_frozenmodel():
    print('> Loading frozen model into memory')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        seg_graph_def = tf.GraphDef()
        with tf.gfile.GFile(MODEL_PATH, 'rb') as fid:
            serialized_graph = fid.read()
            seg_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(seg_graph_def, name='')
    return detection_graph


def segmentation(detection_graph, label_names, image, bg="#000000"):
    # fixed input sizes as model needs resize either way
    resize_ratio = 1.0 * 513 / max(image.shape[0], image.shape[1])
    orignal_size = (image.shape[1], image.shape[0])
    target_size = (int(resize_ratio * image.shape[1]), int(resize_ratio * image.shape[0]))
    print("> Starting Segmentaion")

    image = cv2.resize(image, target_size)
    batch_seg_map = sess.run('SemanticPredictions:0',
                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
    # visualization
    seg_map = batch_seg_map[0]
    seg_image = create_colormap(seg_map).astype(np.uint8)
    seg_image = cv2.cvtColor(seg_image, cv2.COLOR_RGB2HSV)
    cv2.imshow("seg", seg_image)
    lower_yellow = np.array([0, 0, 10])
    upper_yellow = np.array([60, 255, 255])
    seg_image = cv2.inRange(seg_image, lower_yellow, upper_yellow)

    # os.system("pause")
    seg_image = cv2.cvtColor(seg_image, cv2.COLOR_GRAY2RGB)
    image = np.bitwise_and(image, seg_image)
    # cv2.addWeighted(seg_image, ALPHA, image, 1 - ALPHA, 0, image)
    # boxes (ymin, xmin, ymax, xmax)
    if BBOX:
        map_labeled = measure.label(seg_map, connectivity=1)
        for region in measure.regionprops(map_labeled):
            if region.area > MINAREA:
                box = region.bbox
                p1 = (box[1], box[0])
                p2 = (box[3], box[2])
                if label_names[seg_map[tuple(region.coords[0])]] != 'person':
                    cv2.rectangle(image, p1, p2, (0, 0, 0), -1)
                # vis_text(image, label_names[seg_map[tuple(region.coords[0])]], (p1[0], p1[1] - 10))
    image = cv2.resize(image, orignal_size)
    if bg != "#000000":
        # 1-2 r  3-4 g 5-6 b
        r, g, b = cv2.split(image)
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if b[i][j] == 0 and g[i][j] == 0 and r[i][j] == 0:
                    color = bg[1:3]
                    r[i][j] = int(color, 16)
                    color = bg[3:5]
                    g[i][j] = int(color, 16)
                    color = bg[5:]
                    b[i][j] = int(color, 16)
        image = cv2.merge((r, g, b)).astype(np.uint8)
    return image


def init():
    download_model()
    global graph
    graph = load_frozenmodel()

    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    graph.as_default()
    global sess
    sess = tf.Session(graph=graph)
