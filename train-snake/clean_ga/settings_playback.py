# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:15:13 2020

@author: rowe1
"""

settings = {
        #(columns,rows) in the grid 
        'grid_size' : (10,10),
        
        'food_energy' : 100,
        
        #how many generations to run for
        'generations' : 20,
        
        #nn_shape[0] is number of nodes in input layer, nn_shape[-1] is number of nodes in output layer
        #All hidden layers have nn_shape[1], nn_shape[2], ... nodes
        'nn_shape' : [18, 14, 8, 4], 
        
        #Activation function to be used at each layer (not including the input layer of course)
        'activation_functions' : ['relu','relu','sigmoid'],
        
        #Location of the best performing neural nets from each generation
        'best_snakes_file' : './ga_snake_history/best'
        
        #set watch to True if you want the screen to display the game as the snakes are trained
        'watch' : True
            }