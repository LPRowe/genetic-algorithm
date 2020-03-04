# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:34:58 2020

@author: Logan Rowe
"""

import snake_game

snake_game.main()

while True:
    if snake_game.game_on==False:
        snake_game.main()