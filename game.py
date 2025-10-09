#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Author      : Bluzy
Date        : 2025/10/07 21:18:01
Contact     : zoe4896@outlook.com
Description : 
'''

import pygame
from manager import GameManager, Systems, Entities
from component import MapComponent, StateComponent, DirectionComponent, PositionComponent, SpeedComponent, InputComponent
import time

# 游戏类
class Game:
    def __init__(self, config_path):
        self.game_manager = GameManager(config_path)
        self.fps = 0
        self._init()

    def _init(self):
        self.systems = Systems(self.game_manager)
        self.entities = Entities(self.game_manager)
        self.running = True
        self.food_entity = self.entities.entity_manager.entities['food']
        self.snake_entity = self.entities.entity_manager.entities['snake']
        self.map = self.entities.entity_manager.entities['map'].get_component(MapComponent)
        self.input_component = self.entities.entity_manager.entities['map'].get_component(InputComponent)
        self.snake_state = self.snake_entity.get_component(StateComponent)
        self.snake_dir = self.snake_entity.get_component(DirectionComponent)
        self.snake_speed = self.snake_entity.get_component(SpeedComponent)
        self.food_pos = self.food_entity.get_component(PositionComponent)
        self.food_state = self.food_entity.get_component(StateComponent)
        self.snake_pos = self.snake_entity.get_component(PositionComponent)
        self.fall_time = pygame.time.get_ticks()

    def _handle_events(self):
        events = pygame.event.get()
        self.systems.sys_input.process(self.snake_dir, self.map, self.input_component)
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.USEREVENT + 2:
                self.running = False
            else:
                continue

    def _update(self):
        current_time = pygame.time.get_ticks()
        self.systems.sys_gen.process(self.snake_state, self.snake_dir, self.food_pos, self.food_state, self.snake_pos)
        if current_time - self.fall_time >= self.snake_speed.y:
            self.systems.sys_movement.process(self.snake_pos, self.snake_speed, self.snake_dir, self.snake_state, self.input_component, self.food_state)
            condition = self.systems.sys_collision.process(self.snake_pos, self.snake_state, self.food_pos, self.food_state)
            self.systems.sys_goal.process(self.map, self.food_state)
            if condition == 3:
                self.systems.sys_gen.process(self.snake_state, self.snake_dir, self.food_pos, self.food_state, self.snake_pos)
            self.systems.sys_map.process(self.map, self.snake_state, self.food_pos, self.food_state)
            self.fall_time = current_time
    def _render(self):
        self.systems.sys_render.process(self.map)

    def run(self):
        while self.running:
            self._handle_events()
            if not self.map.paused and not self.map.game_over:
                if not self.map.restart:
                    self._update()
                    self._render()
                else:
                    self._init()
            elif self.map.game_over:
                self._render()
            elif self.map.paused:
                self._render()
            pygame.display.update()
            self.game_manager.clock.tick(self.game_manager.config.FPS)
        pygame.quit()