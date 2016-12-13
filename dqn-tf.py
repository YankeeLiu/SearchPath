import tensorflow as tf
import numpy as np
import time
import MazeGame as mg
import os
import imgqueue
from tensorflow.python.platform import gfile
from random import sample


flags = tf.app.flags
FLAGS = flags.FLAGS
# FLAGS.DEFINE_string("summaries_dir", "./tmp/save_graph_loss",
#                     "Summaries directory")

imgRow, imgCol = 100, 100
imgChannel = 4
actionNum = 4
initDistance = 1
batchSz = 64
gamma = 0.99
observe = 320
Epsilon = 0.4
resetLimitaion = 300000
blkSz = 3
distance = 2
difficulty = 5
scale = 20
renderScale = 5
renderSize = imgRow * renderScale
TRAIN_EPOCH = 20
DROPOUT_RATE = 0.25


def weight_variable(shape):

    initial = tf.truncated_normal(shape=shape, stddev=0.1)

    return tf.Variable(initial)


def bias_variable(shape):

    initial = tf.constant(0.1, shape=shape)

    return tf.Variable(initial)


def conv2d(x, conv_kernel, padding):

    conv2d = tf.nn.conv2d(input=x, filter=conv_kernel, strides=[
                          1, 1, 1, 1], padding=padding)
    return conv2d


def max_pool(x, sampling_size):

    max_pool = tf.nn.max_pool(value=x, ksize=sampling_size, strides=[
                              1, 2, 2, 1], padding="SAME")
    return max_pool


x = tf.placeholder(tf.float32, shape=[None, imgRow, imgCol, imgChannel])
keep_prob = tf.placeholder(tf.float32)


def DQN():
    W_conv1 = weight_variable([5, 5, 4, 128])
    b_conv1 = bias_variable([128])

    h_conv1 = tf.nn.relu(conv2d(x, W_conv1, padding="SAME") + b_conv1)

    W_conv2 = weight_variable([3, 3, 128, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2, padding="SAME") + b_conv2)

    W_conv3 = weight_variable([3, 3, 64, 32])
    b_conv3 = bias_variable([32])

    h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3, padding="SAME") + b_conv3)

    W_fc1 = weight_variable([100 * 100 * 32, 512])
    b_fc1 = bias_variable([512])

    h_conv3_flatten = tf.reshape(h_conv3, shape=[-1, 100 * 100 * 32])
    h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flatten, W_fc1) + b_fc1)

    W_fc2 = weight_variable([512, 64])
    b_fc2 = bias_variable([64])

    h_fc2 = tf.nn.relu(tf.matmul(h_fc1, W_fc2) + b_fc2)
    h_fc2_drop = tf.nn.dropout(h_fc2, keep_prob)

    W_y = weight_variable([64, actionNum])
    b_y = bias_variable([actionNum])

    y_out = tf.matmul(h_fc2_drop, W_y) + b_y

    return y_out

labels = tf.placeholder(tf.float32, shape=[None, actionNum])


def loss(predicts, labels):

    mse = tf.reduce_mean(tf.square(predicts - labels))

    return mse


def train(loss_op):

    optimizer = tf.train.AdamOptimizer(1e-5)
    train_op = optimizer.minimize(loss_op)

    return train_op


def __main__():

    print "building model"

    # Create a new maze
    mz = mg.Maze()
    mz.createNewMaze(difficulty, scale, distance, blkSz)

    # initialized two counters
    counter = -1
    reset_time = -1

    # set epsilp-random rate
    randomEpsilon = Epsilon

    # initialized a imag manager
    queueImg = imgqueue.imgQueue()

    # initialized a render
    mz.initialRender(renderSize, renderSize, renderScale)

    # set GPU profile
    # config = tf.ConfigProto()
    # config.gpu_options.allow_growth = True

    output_action = DQN()
    loss_op = loss(output_action, labels)
    train_op = train(loss_op)

    sess = tf.Session()

    sess.run(tf.global_variables_initializer())

    inputs = np.zeros((batchSz, imgRow, imgCol, imgChannel), dtype="float")
    targets = np.zeros((batchSz, actionNum), dtype="float")

    print "preparing game"

    while(True):

        # initalized some flags
        reset_time += 1
        counter = 0
        queueImg.resetQueue()
        # Create continual 4 gray image

        # pick random start & end postion
        init_image = mz.getMazeState()
        mz.loactedStartPoint()

        for i in range(imgChannel):
            queueImg.append(init_image)

        # change the difficulty  &  random rate
        mz.setDistance((distance + 1))

        while (counter < resetLimitaion):

            mz.loactedStartPoint()
            # making decision
            # choose action randomly

            feed_dict = {
                x: queueImg.getChannels(),
                keep_prob: DROPOUT_RATE
            }

            if np.random.random() < randomEpsilon:
                random_action_t = np.random.randint(0, actionNum)
                action_t = random_action_t

            else:

                # choose the max prediction reward
                predict_action = sess.run(output_action, feed_dict=feed_dict)
                predicted_action_t = np.argmax(predict_action)
                action_t = predicted_action_t

            # change the postion depends on action index

            terminated, reward_t = mz.moveToNextState(action_t)

            # get the next state
            image = mz.getMazeState()

            # rende current state
            mz.visualization(imgRow, imgCol)

            # add the newest state
            queueImg.append(image)

            if terminated:
                # if knock into the wall
                queueImg.addInfo((action_t, reward_t))

            else:
                # calculate reward
                grayImages_t = queueImg.getChannels()

                feed_dict = {
                    x: grayImages_t,
                    keep_prob: DROPOUT_RATE
                }

                reward_t += gamma * \
                    np.max(sess.run(output_action, feed_dict=feed_dict))

                queueImg.addInfo((action_t, reward_t))

            # updating counter
            counter += 1

            if counter < observe:
                continue

            #============TRAIN============#

            for k in xrange(batchSz):
                choise = np.random.randint(0, len(queueImg) - 1)
                inputs[k] = queueImg.getChannels(choise)
                info = queueImg.getInfo(choise)
                action_history = info[0]
                reward_history = info[1]

                feed_dict = {
                    x: inputs[k].reshape((1, imgRow, imgCol, imgChannel)),
                    keep_prob: DROPOUT_RATE
                }

                targets[k] = sess.run(output_action, feed_dict=feed_dict)
                targets[k][action_history] = reward_history

            loss_feed_dict = {
                x: inputs,
                labels: targets,
                keep_prob: DROPOUT_RATE
            }

            loss_value = np.mean(sess.run([train_op, loss_op],
                                          feed_dict=loss_feed_dict))

            # if counter % 10 == 0:
            # print reset_time, counter, "loss = %.4f" % loss_value


if __name__ == "__main__":
    __main__()
