# -*- coding:utf-8 -*-
import numpy as np
import time
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import Adam
import MazeGame

imgRow , imgCol = 100, 100
imgChannel = 1
actionNum = 4
initDistance = 1
batchSz = 32
gamma = 0.99

def getModel():
    model = Sequential()
    model.add(Convolution2D(32, 3, 3, subsample=(2, 2), init="uniform", border_mode='same', input_shape=(imgChannel, imgRow, imgCol)))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, subsample=(2, 2), init="uniform", border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3, subsample=(2, 2), init="uniform", border_mode='same'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dense(512, init="uniform"))
    model.add(Activation('relu'))
    model.add(Dense(actionNum, init="uniform"))

    adam = Adam(lr=1e-6)
    model.compile(loss='mse', optimizer=adam)
    return model

def train(model):
    mazeGame = MazeGame.mazeState()    # 和迷宫当前状态相关的数据获取
    mazeGame.createNewMaze()
    counter = 0    # 计数器
    maxDistance = initDistance

    while(True):

        inputs = np.zeros((batchSz, imgChannel, imgRow, imgCol))  # 32, 1, 80, 80
        targets = np.zeros((inputs.shape[0], actionNum))  # 32, 4

        nowX, nowY, endX, endY = mazeGame.selectStartAndEndPoint(maxDistance)
        mazeGame.calRewadMatrix(endX,endY)

        for i in range(batchSz):
            inputs[i] = mazeGame.getCurrentImage(nowX, nowY, endX, endY)    # 获取当前图像
            targets[i] = model.predict(inputs[i].reshape([1, 1, imgRow, imgCol]))    # 网络走一步
            action_t = np.argmax(targets[i])    # reward预测值最大的那一步
            # print targets[i]
            # 按照网络预测走一步state.
            back_x = nowX
            back_y = nowY

            if action_t == 0:
                nowY -= 1
            elif action_t == 1:
                nowY += 1
            elif action_t == 2:
                nowX -= 1
            else:
                nowX += 1

            terminated, reward_t = mazeGame.getReward(nowX, nowY)        #当前这步真实的reward

            if terminated:
                # 如果撞墙了或者走到终点了
                targets[i][action_t] = reward_t
                nowX = back_x
                nowY = back_y

            else:
                # 要计算下一步reward
                image_t1 = mazeGame.getCurrentImage(nowX, nowY, endX, endY)
                image_t1 = image_t1.reshape([1, 1, imgRow, imgCol])
                targets[i][action_t] = reward_t + gamma * np.max(model.predict(image_t1))
                #print action_t, targets[i]

        loss = model.train_on_batch(inputs, targets)

        if counter % 100 == 0:
            maxDistance += 1

        if counter % 10 == 0:
            print "loss = %.4f" % loss

        if counter % 100 == 0:
            test_x, test_y, test_end_x, test_end_y = mazeGame.selectStartAndEndPoint(maxDistance)
            test_terminated = False
            test_Reward = mazeGame.calRewadMatrix(endX, endY)
            count = 0
            while(test_terminated==False or count <= 30):

                test_state = mazeGame.getCurrentImage(test_x, test_y, test_end_x, test_end_y)
                mazeGame.visualization(test_state)
                test_action = np.argmax(model.predict(test_state.reshape([1, 1, imgRow, imgCol])))



                if test_action == 0:
                    test_y -= 1
                elif test_action == 1:
                    test_y += 1
                elif test_action == 2:
                    test_x -= 1
                else:
                    test_x += 1

                    test_terminated, test_Reward = mazeGame.getReward(test_x, test_y)  # 当前这步真实的reward

                if test_terminated:
                    break

        if counter % 5000 == 0:
            # 每1000次换一个地图
            maxDistance = initDistance
            mazeGame.createNewMaze()
            # 保存一下权值
            model.save_weights("model.h5", overwrite=True)


        counter += 1    # 递增计数器

def __main__():
    model = getModel()
    train(model)

if __name__ == "__main__":
    __main__()
    



