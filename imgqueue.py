from collections import deque
import numpy as np


replayMemory = 25000
imgChannel = 4
imgRow, imgCol = 100, 100


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

        return grayImages_t.reshape([1, imgRow, imgCol, imgChannel])

    def getInfo(self, position=-1):
        return self.__info[position]

    def __len__(self):
        return len(self.__queue) - imgChannel + 1

    def resetQueue(self):
        self.__queue.clear()
        self.__info.clear()
