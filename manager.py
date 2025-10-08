#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Author      : Bluzy
Date        : 2025/10/07 21:18:08
Contact     : zoe4896@outlook.com
Description : 
'''

import yaml
import pygame
import numpy as np
from types import SimpleNamespace
from entity import EntityManager
from system import InputSystem, MovementSystem, CollisionSystem, RenderSystem, MapSystem, GenerateSystem
from component import PositionComponent, SpeedComponent, ColorComponent, StateComponent, MapComponent, DirectionComponent, InputComponent

class GameManager:
    def __init__(self, config_path) -> None:
        pygame.init()
        pygame.display.set_caption("The Snake")
        self.config = self._get_config_from_yaml(config_path)
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), vsync=True)
        self.clock = pygame.time.Clock()

    def _get_config_from_yaml(self, file_path):
        config = self._dict_to_struct(yaml.safe_load(open(file_path, 'r')))
        return config
    
    def _dict_to_struct(self, d):
        return SimpleNamespace(**{k: self._dict_to_struct(v) if isinstance(v, dict) else v for k, v in d.items()})
    
class Systems:
    def __init__(self, game_manager) -> None:
        self.game_manager = game_manager
        self.config = game_manager.config
        self.sys_input = InputSystem()
        self.sys_movement = MovementSystem()
        self.sys_collision = CollisionSystem(self.config)
        self.sys_render = RenderSystem(self.game_manager.screen, self.config)
        self.sys_map = MapSystem(self.config)
        self.sys_gen = GenerateSystem(self.config)

class Entities:
    def __init__(self, game_manager) -> None:
        self.game_manager = game_manager
        self.config = game_manager.config
        self.entity_manager = EntityManager()
        self._init_snake()
        self._init_map()

    def _init_snake(self):
        self.create_entity(
            'snake',
            DirectionComponent(),
            PositionComponent(),
            SpeedComponent(0, self.config.INIT_SPEED), 
            ColorComponent((0,255,0)), 
            StateComponent()
        )
        self.create_entity(
            'food',
            PositionComponent(),
            ColorComponent((255,0,0)), 
            StateComponent()
        )

    def _init_map(self):
        self.create_entity(
            'map',
            MapComponent(np.zeros((self.config.PLAYFIELD_WIDTH, self.config.PLAYFIELD_HEIGHT), dtype=int), self.config.INIT_SPEED, self.config.LEVEL),
            InputComponent()
        )

    def create_entity(self, entity_type, *components):
        entity = self.entity_manager.create_entity(entity_type)
        for component in components:
            entity.add_component(component)
