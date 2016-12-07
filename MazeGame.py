# -*- coding:utf-8 -*-

from ctypes import *
import numpy as np
import time

MAP_SIZE = 100
Objdll = CDLL("./libtool.so")

num_to_people = 0.5
num_to_wall = -1
num_to_road = 0.1
num_to_finish = 1

num_board_postive = 3
num_board_negetive = -2

class mazeState():

    maze = np.zeros([MAP_SIZE, MAP_SIZE])
    reward = np.zeros([MAP_SIZE, MAP_SIZE])

    def __init__(self):
        pass

    # 创建一个新的迷宫 random_map为二维矩阵
    def createNewMaze(self):
        bufferMap = Objdll.createIntBuffer(MAP_SIZE * MAP_SIZE)
        Objdll.getRandomMaze(bufferMap, 5, 20);

        for x in range(MAP_SIZE):
            for y in range(MAP_SIZE):
                self.maze[x][y] = Objdll.getValue(bufferMap, (x + y * MAP_SIZE))

        Objdll.destroyIntBuffer(bufferMap)

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
            start_point_x = end_point_x + np.random.randint(low=-maxDistance, high=maxDistance)
            start_point_y = end_point_y + np.random.randint(low=-maxDistance, high=maxDistance)


        return start_point_x, start_point_y, end_point_x, end_point_y

    #x y分别代表““人”所在位置的横竖坐标，在地图上做标记后返回
    def getCurrentImage(self, s_x, s_y, e_x, e_y):

        current_image = np.zeros([MAP_SIZE, MAP_SIZE])

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                current_image[i][j] = num_to_wall if self.maze[i][j] == -1 else num_to_road

        for i in range(num_board_negetive, num_board_postive):
            for j in range(num_board_negetive, num_board_postive):
                current_image[s_x + i][s_y + j] = num_to_people
                current_image[e_x + i][e_y + j] = num_to_finish

        #current_image = current_image.reshape([1, MAP_SIZE, MAP_SIZE])

        return current_image

    #计算reward矩阵,输入为终点坐标
    def calRewardMatrix(self, x, y):
        max_distance = 0
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                distance = np.sqrt((i - x) ** 2 + (j - y) ** 2)
                if distance > max_distance:
                    max_distance = distance

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if (self.maze[i][j] == -1):
                    self.reward[i][j] = -1
                elif self.maze[i][j] == 1:
                    self.reward[i][j] = 1 - np.sqrt((i - x) ** 2 + (j - y) ** 2) / max_distance
        self.reward[x][y] = 10.0

    #返回一个一个操作对应的reward值和是否结束
    def getReward(self, x, y):
        terminated = False
        if self.reward[x][y] == -1 or self.reward[x][y] == 1:
            terminated = True
        return terminated, self.reward[x][y]

    def visualization(self, m):
        bufferMapR = Objdll.createIntBuffer(MAP_SIZE * MAP_SIZE)

        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                Objdll.setValue(bufferMapR, j + i * MAP_SIZE, Objdll.rgb(0, int(np.abs(m[i][j] * 255)), 0))

        Objdll.initRenderer(800, 800, 32, 8)
        Objdll.render(bufferMapR, 100, 100)

        Objdll.handleEvents()
        time.sleep(0.1)  # 0.1s

        Objdll.destroyIntBuffer(bufferMapR)


def __main__():

    state = mazeState()
    state.createNewMaze()
    s_x, s_y, e_x, e_y = state.selectStartAndEndPoint(maxDistance=10)
    image = state.getCurrentImage(s_x, s_y, e_x, e_y)
    state.calRewardMatrix(x=e_x, y=e_y)
    state.visualization(image)
    time.sleep(2)
    state.visualization(state.reward)
    time.sleep(2)

if __name__ == "__main__":
    __main__()

