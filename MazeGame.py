# -*- coding:utf-8 -*-

from ctypes import *
import numpy as np
import time

BATCH_SIZE = 32
MAP_SIZE = 100
Objdll = CDLL("./libtool.so")

num_to_people = 0.5
num_to_wall = -1
num_to_road = 0
num_to_finish = 1

num_board_postive = 6
num_board_negetive = -5


class Maze():

    maze = np.zeros([MAP_SIZE, MAP_SIZE])

    def __init__(self):
        pass

    # 创建一个新的迷宫 random_map为二维矩阵
    def createNewMaze(self):
        bufferMap = Objdll.createIntBuffer(MAP_SIZE * MAP_SIZE)
        Objdll.getRandomMaze(bufferMap, 10, 10)

        for i in range(MAP_SIZE):
            for k in range(MAP_SIZE):
                self.maze[i][k] = Objdll.getValue(
                    bufferMap, (k + i * MAP_SIZE))

        Objdll.destroyIntBuffer(bufferMap)
        return self.maze

    # 随机初始化开始坐标和结束坐标，返回坐标数据
    def selectStartAndEndPoint(self, maxDistance):

        end_point = -1
        end_point_x = 0
        end_point_y = 0
        while (end_point_x >= MAP_SIZE - num_board_postive or end_point_y >= MAP_SIZE - num_board_postive or end_point_x <= num_board_postive or end_point_y <= num_board_postive
               or end_point == -1 or self.maze[end_point_x][end_point_y] == -1):
            end_point = int(np.random.random() * (MAP_SIZE ** 2))
            end_point_x = end_point / MAP_SIZE
            end_point_y = end_point % MAP_SIZE

        start_point_x = 0
        start_point_y = 0
        while(start_point_x >= MAP_SIZE - num_board_postive or start_point_y >= MAP_SIZE - num_board_postive or start_point_x <= num_board_postive or start_point_y <= num_board_postive
              or self.maze[start_point_x][start_point_y] == -1):
            start_point_x = end_point_x + \
                np.random.randint(low=-maxDistance, high=maxDistance)
            start_point_y = end_point_y + \
                np.random.randint(low=-maxDistance, high=maxDistance)

        return start_point_x, start_point_y, end_point_x, end_point_y

    # x y分别代表““人”所在位置的横竖坐标，在地图上做标记后返回
    def getCurrentImage(self, s_x, s_y, e_x, e_y):

        currtent_image = np.zeros([MAP_SIZE, MAP_SIZE])

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                currtent_image[i][j] = num_to_wall if self.maze[
                    i][j] == -1 else num_to_road

        for i in range(num_board_negetive, num_board_postive):
            for j in range(num_board_negetive, num_board_postive):
                currtent_image[s_x + i][s_y + j] = num_to_people
                currtent_image[e_x + i][e_y + j] = num_to_finish

        currtent_image = currtent_image.reshape([1, MAP_SIZE, MAP_SIZE])

        return currtent_image

    # 计算reward矩阵,输入为终点坐标
    def calRewardMatrix(self, x, y):
        reward = np.zeros([MAP_SIZE, MAP_SIZE])
        max_distance = 0
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                distance = np.sqrt((i - x) ** 2 + (j - y) ** 2)
                if distance > max_distance:
                    max_distance = distance

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if (self.maze[i][j] == -1):
                    reward[i][j] = -100.0
                elif self.maze[i][j] == 1:
                    reward[i][j] = - \
                        (np.sqrt((i - x) ** 2 + (j - y) ** 2) / max_distance)
                #reward[i][j] = (reward[i][j] / 100.0)
        reward[x][y] = 100.0

        return reward

    # 返回一个一个操作对应的reward值和是否结束
    def getReward(self, reward, x, y):
        terminated = False
        if reward[x][y] == -100.0 or reward[x][y] == 100.0:
            terminated = True
        return terminated, reward[x][y]

    def visualization(self, m):
        bufferMapR = Objdll.createIntBuffer(MAP_SIZE * MAP_SIZE)

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                Objdll.setValue(bufferMapR, j + i * MAP_SIZE,
                                Objdll.rgb(0, int(np.abs(m[0][i][j] * 255)), 0))

        Objdll.initRenderer(800, 800, 32, 8)
        Objdll.render(bufferMapR, 100, 100)

        Objdll.handleEvents()
        # time.sleep(0.1)  # 0.1s

        Objdll.destroyIntBuffer(bufferMapR)

    def moveToNextState(self, action):
        terminated = False
        val = Objdll.move(action)
        if val == -1:
            terminated = True

        return terminated, val

    def getMazeState():
        image = Objdll.getImage()
        return image


def __main__():
    state = mazeState()
    state.createNewMaze()
    s_x, s_y, e_x, e_y = state.selectStartAndEndPoint(maxDistance=10)
    image = state.getCurrentImage(s_x, s_y, e_x, e_y)
    reward = state.calRewardMatrix(x=e_x, y=e_y)
    state.visualization(image)
    time.sleep(1)
    state.visualization(reward.reshape((1, 100, 100)))
    time.sleep(100)


if __name__ == "__main__":
    __main__()
