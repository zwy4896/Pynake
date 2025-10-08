#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Author      : Bluzy
Date        : 2025/10/07 21:18:16
Contact     : zoe4896@outlook.com
Description : 
'''

import pygame
import numpy as np
import random
# 输入系统
class InputSystem:
    def __init__(self) -> None:
        self.key_mapping = {
            pygame.K_LEFT: 'left',
            pygame.K_RIGHT: 'right',
            pygame.K_DOWN: 'down',
            pygame.K_UP: 'up',
            pygame.K_SPACE: 'hard_drop',
            pygame.K_TAB: 'pause',
            pygame.K_RETURN: 'restart',
        }
        self.handlers = {
            'running': self._handle_running,
            'paused': self._handle_paused,
            'game_over': self._handle_game_over
        }
        self.prev_keys = pygame.key.get_pressed()
    def process(self, direction, map_comp, input_component):
        keys = pygame.key.get_pressed()
         # 遍历按键映射表，只检测“按下瞬间”的键（从未按 → 按下）
        for key, action in self.key_mapping.items():
            if keys[key] and not self.prev_keys[key]:
                # 瞬时触发一次
                self.handle_key_event(key, direction, map_comp, input_component)
        self.prev_keys = keys  # 刷新按键状态

    def handle_key_event(self, key, direction, map_comp, input_component):
        action = self.key_mapping.get(key)
        if not action:
            print(action)
            return

        state = 'game_over' if map_comp.game_over else 'paused' if map_comp.paused else 'running'
        self.handlers[state](action, direction, map_comp, input_component)
    def _handle_running(self, action, direction, map_comp, input_component):
        if action in ['left', 'right', 'up', 'down']:
            if self.is_opposite(action, direction.direction):
                input_component.next_direction = action
        elif action == 'pause':
            map_comp.paused = True
        elif action == 'restart':
            map_comp.game_over = False
            map_comp.restart = True

    def _handle_paused(self, action, direction, map_comp, input_component):
        if action == 'pause':
            map_comp.paused = False
        elif action == 'restart':
            map_comp.game_over = False
            map_comp.restart = True

    def _handle_game_over(self, action, direction, map_comp, input_component):
        if action == 'restart':
            map_comp.game_over = False
            map_comp.restart = True

    def is_opposite(self, new, current):
        # 检查新方向是否与当前方向相反
        return (new == 'up' and current != 'down') or \
               (new == 'down' and current != 'up') or \
               (new == 'left' and current != 'right') or \
               (new == 'right' and current != 'left')
# 移动系统
class MovementSystem:
    def process(self, position, speed, direction, state, input_component):
        if state.is_blocked:
            state.is_blocked = not state.is_blocked
        if state.is_alive:
            self.apply_direction(direction, input_component)
            if direction.direction == 'left':
               position.x -= 1
            elif direction.direction == 'right':
                position.x += 1
            elif direction.direction == 'up':
                position.y -= 1
            elif direction.direction == 'down':
                position.y += 1
            new_head = (position.x, position.y)
            state.shape.insert(0, new_head)

    def apply_direction(self, direction, input_component):
        # 在蛇移动前调用，将 next_direction 应用
        if input_component.next_direction:
            direction.direction = input_component.next_direction
            input_component.next_direction = None
# 碰撞检测系统
class CollisionSystem(MovementSystem):
    def __init__(self, config) -> None:
        super().__init__()
        self.playfield_width = config.PLAYFIELD_WIDTH
        self.playfield_height = config.PLAYFIELD_HEIGHT
    
    def process(self, snake_position, snake_state, food_position, food_state):
        print('BLOCKED!!!!!',snake_state.is_blocked)
        print('EATEN##############',food_state.eaten)
        if not snake_state.is_blocked:
            head = (snake_position.x, snake_position.y)
            if not (snake_position.x in range(0, self.playfield_width) and snake_position.y in range(0, self.playfield_height)):
                # 与边界碰撞，状态=碰撞，死亡
                snake_state.collision = True
                snake_state.is_alive = False
                snake_state.is_blocked = True
                return 1
            if head in snake_state.shape[1:]:
                # 自身碰撞
                snake_state.collision = True
                snake_state.is_alive = False
                snake_state.is_blocked = True
                return 2
            if food_position.x == snake_position.x and food_position.y == snake_position.y:
                # 吃到食物
                snake_state.collision = True
                snake_state.is_alive = True
                snake_state.is_blocked = True
                food_state.collision = True
                food_state.is_alive = False
                food_state.active = False
                food_state.eaten = True
                return 3
            else:
                food_state.eaten = False
                snake_state.collision = False
                snake_state.is_alive = True
                snake_state.is_blocked = False
                return 0
        else:
            return 0
            
# 渲染系统
class RenderSystem:
    def __init__(self, screen, config):
        self.screen = screen
        self.block_size = config.BLOCK_SIZE
        self.color = eval(config.COLOR)
        self.real_block_size = self.block_size-4
        self.font = pygame.font.Font(None, 36)
        self.play_field = pygame.Surface((config.PLAYFIELD_WIDTH*self.block_size, config.PLAYFIELD_HEIGHT*self.block_size))
        self.score_board = pygame.Surface((config.SCREEN_WIDTH - config.PLAYFIELD_WIDTH*self.block_size, config.SCOREBOARD_HEIGHT))
        self.game_over_text = self.font.render("Y o u  D i e d !", True, (255, 0, 0))
        self.game_over_text_rect = self.game_over_text.get_rect(center=(self.play_field.get_width() // 2, self.play_field.get_height() // 2))
        self.pause_text = self.font.render("P A U S E D", True, (255, 0, 0))
        self.pause_text_rect = self.game_over_text.get_rect(center=(self.play_field.get_width() // 2, self.play_field.get_height() // 2))
        self.grid_surface = pygame.Surface((self.play_field.get_width(), self.play_field.get_height()), pygame.SRCALPHA)
        # self.grid_surface.set_colorkey((0, 0, 0))
        self._render('all')

    def process(self, map_mat):
        self._render('play_field')
        self._draw_grid()
        self._render_block(map_mat.snake_map, map_mat.color_map)
        if map_mat.game_over:
            self._render_game_over()
        if map_mat.paused:
            self._render_pause()
    def _draw_grid(self):
        for x in range(0, self.play_field.get_width(), self.block_size):
            pygame.draw.line(self.grid_surface, (100,156,200,255), (x, 0), (x, self.play_field.get_height()),3)
        for y in range(0, self.play_field.get_height(), self.block_size):
            pygame.draw.line(self.grid_surface, (100,156,200,255), (0, y), (self.play_field.get_width(), y),3)
        self.screen.blit(self.grid_surface, (0,0))
    def _render_pause(self):
        self.screen.blit(self.pause_text, self.pause_text_rect)

    def _render_block(self, pos_mat, color_mat):
        nonzero_indices = np.where(pos_mat != 0)
        for x, y in zip(nonzero_indices[0], nonzero_indices[1]):
            block_rect = pygame.Rect(x*self.block_size+2, y*self.block_size+2, self.real_block_size, self.real_block_size)
            pygame.draw.rect(self.screen, color_mat[pos_mat[x][y]], block_rect)
    
    def _render_score(self):
        self._render('score_board')
        score_text = self.font.render(str(self.map_mat.score), True, (0,0, 255))
        score_rect = score_text.get_rect(center=(self.screen.get_width() - self.score_board.get_rect().centerx, self.score_board.get_rect().centery//2))
        self.screen.blit(score_text, score_rect)
    
    def _render(self, mode = 'all'):
        if mode == 'play_field' or mode == 'all':
            self.play_field.fill(self.color[1])
            self.screen.blit(self.play_field, (0,0))
        if mode == 'score_board' or mode == 'all':
            self.score_board.fill((255,255,255))
            self.screen.blit(self.score_board, (self.screen.get_width()-self.score_board.get_size()[0], 0))
    def _render_game_over(self):
        self.screen.blit(self.game_over_text, self.game_over_text_rect)

class MapSystem:
    def __init__(self, config) -> None:
        self.config = config
    def process(self, map_mat, snake_state, food_position, food_state):
        # 1: snake
        # 2: food
        # 3: obstacle

        map_mat.map_cache = map_mat.snake_map.copy()
        if snake_state.is_alive:
            nonzero_indices = np.where(map_mat.snake_map != 0)
            map_mat.map_cache[nonzero_indices] = 0
            if not food_state.eaten:
                if len(snake_state.shape)>1:
                    snake_state.shape.pop()
            for (x,y) in snake_state.shape:
                map_mat.map_cache[x][y] = self.config.SNAKE_IDX
            map_mat.map_cache[food_position.x][food_position.y] = self.config.FOOD_IDX
            map_mat.snake_map = map_mat.map_cache
        else:
            map_mat.game_over = True

class GenerateSystem:
    def __init__(self, config) -> None:
        self.config = config
    def process(self, snake_state, snake_dir, food_pos, food_state, snake_pos):
        if not food_state.active:
            food_pos.x = random.randint(0, self.config.PLAYFIELD_WIDTH-1)
            food_pos.y = random.randint(0, self.config.PLAYFIELD_HEIGHT-1)
            # food_pos.x = 10
            # food_pos.y = 12
            food_state.active = True
            food_state.is_alive = True
            food_state.collision = False
        if not snake_state.active:
            snake_pos.x = 8
            snake_pos.y = 12
            snake_state.active = True
            snake_state.is_alive = True
            snake_dir.direction = 'right'
            snake_state.shape.insert(0, (snake_pos.x, snake_pos.y))
class test_GenerateSystem:
    def __init__(self, config) -> None:
        self.config = config
    def process(self, snake_state, snake_dir, food_pos, food_state, snake_pos):
        if not food_state.active:
            food_pos.x = random.randint(0, self.config.PLAYFIELD_WIDTH-1)
            food_pos.y = random.randint(0, self.config.PLAYFIELD_HEIGHT-1)
            # food_pos.x = 15
            # food_pos.y = 12
            food_state.active = True
            food_state.is_alive = True
            food_state.collision = False
        if not snake_state.active:
            snake_pos.x = 8
            snake_pos.y = 12
            snake_state.active = True
            snake_state.is_alive = True
            snake_dir.direction = 'right'
            snake_state.shape.insert(0, (snake_pos.x, snake_pos.y))