#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Author      : Bluzy
Date        : 2025/10/03 18:42:57
Contact     : zoe4896@outlook.com
Description : 
'''

from game import Game

if __name__ == '__main__':
    game = Game('config.yaml')
    game.run()