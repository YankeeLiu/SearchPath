import tensorflow as tf
import numpy as np
import time
import MazeGame as mg
import os
import imgqueue
from tensorflow.python.platform import gfile
from random import sample

imgRow, imgCol = 100, 100
imgChannel = 4
actionNum = 4
initDistance = 1
batchSz = 1
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


def avg_pool(x, sampling_size):

    avg_pool = tf.nn.avg_pool(value=x, ksize=sampling_size, strides=[
        1, 2, 2, 1], padding="SAME")
    return avg_pool


x = tf.placeholder(tf.float32, shape=[None, imgRow, imgCol, imgChannel])


def DQN():
    W_conv1 = weight_variable([5, 5, 4, 32])
    b_conv1 = bias_variable([32])

    h_conv1 = tf.nn.relu(conv2d(x, W_conv1, padding="SAME") + b_conv1)

    W_conv2 = weight_variable([3, 3, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2, padding="SAME") + b_conv2)

    W_conv3 = weight_variable([3, 3, 64, 32])
    b_conv3 = bias_variable([32])

    h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3, padding="SAME") + b_conv3)
    h_avg_pool3 = avg_pool(h_conv3, sampling_size=[1, 2, 2, 1])

    W_fc1 = weight_variable([50 * 50 * 32, 512])
    b_fc1 = bias_variable([512])

    h_conv3_flatten = tf.reshape(h_avg_pool3, shape=[-1, 50 * 50 * 32])
    h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flatten, W_fc1) + b_fc1)

    W_fc2 = weight_variable([512, 64])
    b_fc2 = bias_variable([64])

    h_fc2 = tf.nn.relu(tf.matmul(h_fc1, W_fc2) + b_fc2)

    W_y = weight_variable([64, actionNum])
    b_y = bias_variable([actionNum])

    y_out = tf.matmul(h_fc2, W_y) + b_y

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
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True

    output_action = DQN()
    loss_op = loss(output_action, labels)
    train_op = train(loss_op)

    sess = tf.Session(config=config)

    saver = tf.train.Saver()

    sess.run(tf.global_variables_initializer())


    inputs = np.zeros((batchSz, imgRow, imgCol, imgChannel), dtype="float")
    targets = np.zeros((batchSz, actionNum), dtype="float")
    predict_action_reward = np.zeros(shape=[1, 4], dtype="float")

    print "preparing game"

    while(True):

        if os.path.exists('./model/model.tfmodel'):
            print "Loading Model"
            saver.restore(sess, './model/model.tfmodel')

        # initalized some flags
        reset_time += 1
        counter = 0
        queueImg.resetQueue()
        # Create continual 4 gray image

        # pick random start & end postion
        init_image = mz.getMazeState()

        for i in range(imgChannel):
            queueImg.append(init_image)

        # change the difficulty  &  random rate
        mz.setDistance((distance + 1))

        while (counter < resetLimitaion):

            # making decision
            # choose action randomly

            image = queueImg.getChannels()

            if np.random.random() < randomEpsilon:

                random_action_t = np.random.randint(0, actionNum)
                action_t = random_action_t
                predict_action_reward = [0, 0, 0, 0]

            else:

                feed_dict = {
                    x: image,
                }
                # choose the max prediction reward
                predict_action = sess.run(output_action, feed_dict=feed_dict)
                predict_action_reward = predict_action
                predicted_action_t = np.argmax(predict_action)
                action_t = predicted_action_t

            # change the postion depends on action index

            terminated, reward_t = mz.moveToNextState(action_t)

            # print action_t, reward_t, predict_action_reward

            # get the next state
            image = mz.getMazeState()

            # rende current state
            mz.visualization(imgRow, imgCol)

            # add the newest state
            queueImg.append(image)

            if terminated:
                # if knock into the wall
                queueImg.addInfo((predict_action_reward, action_t, reward_t))

            else:
                # calculate reward
                grayImages_t = queueImg.getChannels()

                feed_dict = {
                    x: grayImages_t
                }

                reward_t += gamma * \
                    np.max(sess.run(output_action, feed_dict=feed_dict))

                queueImg.addInfo((predict_action_reward, action_t, reward_t))

            # updating counter
            counter += 1

            if counter < observe:
                continue

            #============TRAIN============#

            for k in xrange(batchSz):
                choise = np.random.randint(0, len(queueImg) - 1)
                inputs[k] = queueImg.getChannels(choise)
                info = queueImg.getInfo(choise)
                targets[k] = info[0]
                action_history = info[1]
                reward_history = info[2]
                targets[k][action_history] = reward_history

            inputs = inputs.reshape([batchSz, imgRow, imgCol, imgChannel])

            loss_feed_dict = {
                x: inputs,
                labels: targets,
            }

            _, loss_value = sess.run([train_op, loss_op],
                                     feed_dict=loss_feed_dict)

            if counter % 10 == 0:
                print "reset_time = %d" % reset_time, "conuter =%d" % counter, "loss =%.4f" % loss_value

            if counter % 250 == 0:
                saver.save(sess, './model/model.tfmodel')


if __name__ == "__main__":
    __main__()
