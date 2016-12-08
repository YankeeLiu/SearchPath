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


    def createNewMaze(self, difficulty, scale, distance, blkSz):
        
        self.buffer = Objdll.initGame(difficulty, scale, distance, blkSz)
        
        
    def getState():

        for x in xrange(MAP_SIZE):
            for y in xrange(MAP_SIZE):
                self.maze[x][y] = Objdll.getValue(buffer, x * MAP_SIZE + y)
        return self.maze

    def moveToNextState(self, action):
        terminated = False
        cMove = Objdll.move
        cMove.restype = c_float
        reward = cMove(action)
        if reward < 0:
            terminated = True
        print reward
        return terminated, reward

    def initialRender(self, weight, high, scale):
        Objdll.initRenderer(weight, high, BPP, scale)

    def visualization(self, weight, high):
        Objdll.render(self.buffer, weight, high)


def __main__():
	mg = Maze()
	mg.createNewMaze(10, 10, 3, 2)
	mg.initialRender(500, 500, 5)
	while(Objdll.handleEvents()):
		mg.moveToNextState(1)
		mg.visualization(100, 100)
		#time.sleep(0.1)
		
	




if __name__ == "__main__":
    __main__()
