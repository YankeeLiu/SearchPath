# -*- coding:utf-8 -*-

from ctypes import *
import numpy as np
import time

MAP_SIZE = 100
Objdll = CDLL("./libtool.so")
BPP = 32


class Maze():

    buffer = 0
    maze = np.empty([MAP_SIZE, MAP_SIZE])
    q_value_matrix = np.zeros([MAP_SIZE, MAP_SIZE])
    start_x, start_y, end_x, end_y = 0, 0, 0, 0

    def createNewMaze(self, difficulty, scale, distance, blkSz):

        self.buffer = Objdll.initGame(difficulty, scale, distance, blkSz)

    def getMazeState(self):
        fgetValue = Objdll.getValue
        fgetValue.restype = c_float
        for x in xrange(MAP_SIZE):
            for y in xrange(MAP_SIZE):
                self.maze[x][y] = fgetValue(self.buffer, x * MAP_SIZE + y)
        return self.maze

    def loactedStartPoint(self):
        self.start_x = Objdll.locateCurrentPositionX()
        self.start_y = Objdll.locateCurrentPositionY()
        return self.start_x, self.start_y

    def moveToNextState(self, action):
        terminated = False
        cMove = Objdll.move
        cMove.restype = c_float
        reward = cMove(action)
        if reward == 0.0:
            terminated = True
        return terminated, reward

    def calTempPostion(self, action):
        tmp_x, tmp_y = self.start_x, self.start_y
        if action == 0:
            tmp_x += 1
        elif action == 1:
            tmp_x -= 1
        elif action == 2:
            tmp_y -= 1
        elif action == 3:
            tmp_y += 1
        return tmp_x, tmp_y

    def resetQValueMartix(self):
        self.q_value_matrix = np.zeros([MAP_SIZE, MAP_SIZE]) - 1
        self.q_value_matrix[self.end_x][self.end_y] = 0

    def updateQValueMatrix(self, value):
        self.q_value_matrix[self.start_x][self.start_y] += value

    def requestQValue(self, x, y):
        value = self.q_value_matrix[x][y]
        return value

    def setDistance(self, distance):
        Objdll.setStartEndDistance(distance)

    def initialRender(self, weight, high, scale):
        Objdll.initRenderer(weight, high, BPP, scale)

    def visualization(self, weight, high):
        Objdll.render(self.buffer, weight, high)


def __main__():
    mg = Maze()
    mg.createNewMaze(10, 10, 3, 2)
    mg.initialRender(500, 500, 5)
    i = 0
    while(i < 10000):
        Objdll.handleEvents()
        mg.getMazeState()
        mg.loactedStartPoint()
        mg.moveToNextState(1)
        mg.visualization(100, 100)
        time.sleep(1)
        i += 1


if __name__ == "__main__":
    __main__()
