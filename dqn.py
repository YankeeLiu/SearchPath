# -*- coding:utf-8 -*-
import numpy as np
import time
import MazeGame as mg
from keras.models import Sequential
from keras.initializations import normal
from keras.layers.core import Dense, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import Adam
from collections import deque
from random import sample
import os

imgRow, imgCol = 100, 100
imgChannel = 4
actionNum = 4
initDistance = 1
batchSz = 32
gamma = 0.99
observe = 3200
replayMemory = 20000
Epsilo = 0.3
resetLimitaion = 300000
blkSz = 3
distance = 2
difficulty = 5
scale = 20
renderScale = 5
renderSize = imgRow * renderScale


def getModel():
    model = Sequential()
    model.add(Convolution2D(32, 5, 5, subsample=(2, 2), init=lambda shape, name: normal(
        shape, scale=0.01, name=name), border_mode='same', input_shape=(imgChannel, imgRow, imgCol)))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, subsample=(2, 2), init=lambda shape,
                            name: normal(shape, scale=0.01, name=name), border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3, subsample=(2, 2), init=lambda shape,
                            name: normal(shape, scale=0.01, name=name), border_mode='same'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dense(512, init=lambda shape,
                    name: normal(shape, scale=0.01, name=name)))
    model.add(Activation('relu'))
    model.add(Dense(actionNum, init=lambda shape,
                    name: normal(shape, scale=0.01, name=name)))

    adam = Adam(lr=1e-5)
    model.compile(loss='mse', optimizer=adam)
    return model


class imgQueue:
    def __init__(self):
        self.__queue = deque()
        self.__info = deque()

    def append(self, img):
        if len(self.__queue) >= replayMemory:
            self.__queue.popleft()
        self.__queue.append(img)

    def addInfo(self, info):
        if len(self.__info) >= replayMemory - imgChannel:
            self.__info.popleft()
        self.__info.append(info)

    def getChannels(self, position=-1):
        grayImages_t = np.empty((1, imgChannel, imgRow, imgCol))

        position = len(self.__queue) - \
            imgChannel if position == -1 else position

        for i in range(0, imgChannel):
            # get last 4 image
            grayImages_t[0][i] = self.__queue[i + position]

        return grayImages_t

    def getInfo(self, position=-1):
        return self.__info[position]

    def __len__(self):
        return len(self.__queue) - imgChannel + 1

    def resetQueue(self):
        self.__queue.clear()
        self.__info.clear()


def train(model):

    if os.path.exists("./model.data"):
        model.load_weights("model.data")

    # Create a new maze
    mz = mg.Maze()
    mz.createNewMaze(difficulty, scale, distance, blkSz)

    # initialized two counters
    counter = -1
    reset_time = -1
    # set epsilp-random rate
    randomEpsilon = Epsilo
    # initialized a imag manager
    queueImg = imgQueue()

    inputs = np.zeros((batchSz, imgChannel, imgRow, imgCol))
    targets = np.zeros((batchSz, actionNum))
    mz.initialRender(renderSize, renderSize, renderScale)

    while(True):
        # initalized some flags
        reset_time += 1
        counter += 1
        queueImg.resetQueue()
        # Create continual 4 gray image

	# pick random start & end postion
    	init_image = mz.getMazeState()

        for i in range(imgChannel):
            queueImg.append(init_image)

        #change the difficulty  &  random rate
        mz.setDistance((distance+1))
        randomEpsilon -= 0.01

        while(counter < resetLimitaion):

            # making decision
            if np.random.random() < randomEpsilon:
                # choose action randomly
                action_t = np.random.randint(0, actionNum)
                
            else:
                # choose the max prediction reward
                grayImages_t = queueImg.getChannels()
                predict_action = model.predict(grayImages_t)
                action_t = np.argmax(predict_action)  

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
                reward_t1 = reward_t + gamma * np.max(model.predict(grayImages_t))
                queueImg.addInfo((action_t, reward_t1))

            # refresh counter
            counter += 1

            if counter < observe:
                continue
            #============TRAIN============#

            for i in range(batchSz):
                choise = np.random.randint(0, len(queueImg) - 1)
                inputs[i] = queueImg.getChannels(choise)
                info = queueImg.getInfo(choise)
                action_history = info[0]
                reward_history = info[1]
                targets[i] = model.predict(
                    inputs[i].reshape((1, imgChannel, imgRow, imgCol)))
                targets[i][action_history] = reward_history

            loss = model.train_on_batch(inputs, targets)

            if counter % 10 == 0:
                print reset_time, counter, "loss = %.4f" % loss

            if counter % 1000 == 0:
                # save the weight
                model.save_weights("model.data", overwrite=True)


def __main__():
    model = getModel()
    train(model)


if __name__ == "__main__":
    __main__()
