#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Author      : Bluzy
Date        : 2023/06/26 14:32:19
Contact     : zoe4896@outlook.com
Description : 
'''
import numpy as np

# 定义组件
class InputComponent:
    def __init__(self) -> None:
        self.next_direction = None

class PositionComponent:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class SpeedComponent:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
class ShapeComponent:
    def __init__(self, shape):
        self.shape = shape

class ColorComponent:
    def __init__(self, color):
        self.color = color

class StateComponent:
    def __init__(self, active=False, length = 1) -> None:
        self.active = active
        self.action = ''
        self.collision = False
        self.hard_drop = False
        self.is_blocked = False
        self.length = length
        self.is_alive = True
        self.shape = []
        self.shape_set = set()
        self.eaten = False

class MapComponent:
    def __init__(self, map_mat, speed, level=0) -> None:
        self.pos_map = np.zeros_like(map_mat, dtype=int)
        self.color_map = np.zeros((map_mat.shape[0], map_mat.shape[1], 3), dtype=np.uint8)
        self.snake_pos_cache = []
        self.food_pos_cache = []
        # 颜色定义，0：蛇，1：食物，2：障碍物
        self.color_def = [(0,255,0), (166,255,40), (255,255,0), (255, 150, 255)]
        self.paused = False
        self.game_over = False
        self.score = 0
        self.restart = False
        self.level = level
        self.new_head = None
        self.tail = None
        self.score = 0
class DirectionComponent:
    def __init__(self, direction='') -> None:
        self.direction = direction