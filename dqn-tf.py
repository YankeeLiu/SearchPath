import tensorflow as tf
import numpy as np
import time
import MazeGame as mg
from random import sample
import os
import imgqueue

imgRow, imgCol = 100, 100
imgChannel = 4
actionNum = 4
initDistance = 1
batchSz = 64
gamma = 0.99
observe = 3200
replayMemory = 20000
Epsilo = 0.4
resetLimitaion = 300000
blkSz = 3
distance = 2
difficulty = 5
scale = 20
renderScale = 5
renderSize = imgRow * renderScale


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)

    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)

    return = tf.Variable(initial)


def conv2d(input, filter, padding):

    conv2d = tf.nn.conv2d(input=input, filter=filter, strides=[
                          1, 1, 1, 1], padding=padding)
    return conv2d


def max_pool(input, shape):
    max_pool = tf.nn.max_pool(input=input, ksize=shape, strides=[
                              1, 2, 2, 1], padding="SAME")


x = tf.placeholder("float", shape=[None, imgRow, imgRow, imgChannel])
_y = tf.placeholder("float", shape=[None, actionNum])
keep_prob = tf.placeholder("float")


def DQN():
    W_conv1 = weight_variable([5, 5, 4, 128])
    b_conv1 = bias_variable([128])

    h_conv1 = tf.nn.relu(conv2d(x, W_conv1) + b_conv1)
    h_pool1 = max_pool(input=h_conv1, shape=[1, 2, 2, 1])

    W_conv2 = weight_variable([3, 3, 128, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool(input=h_conv2, shape=[1, 2, 2, 1])

    W_conv3 = weight_variable([3, 3, 64, 64])
    b_conv3 = bias_variable([32])

    h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3) + b_conv3)
    h_pool3 = max_pool(input=h_conv3, shape=[1, 2, 2, 1])

    W_fc1 = weight_variable([11 * 11 * 64, 512])
    b_fc1 = bias_variable([512])

    h_pool3_flatten = tf.reshape(h_pool3, shape=[-1, 11 * 11 * 64])
    h_fc1 = tf.nn.rele(tf.matmul(h_pool3_flatten, W_fc1) + b_fc1)

    W_fc1 = weight_variable([])
