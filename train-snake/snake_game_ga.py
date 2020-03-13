# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 18:24:35 2020

@author: Logan Rowe
"""

from __future__ import print_function

import pygame
import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
import pickle
import time
import matplotlib.pyplot as plt
import glob

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

pygame.init()

# =============================================================================
# LOAD SOUND EFFECTS AND MUSIC
# =============================================================================



class Snake(object):
    def __init__(self,direction,component,energy):
        
        #{'right':(1,0),'left':(-1,0),'up':(0,1),'down':(0,-1)}
        self.direction=direction
        
        #keep an updated list of the components that make up the snake
        self.components=[component]
        
        #Track the location just behind the tail for when the snake grows
        self.tail=self.components[-1]
        
        #Snake will die of hunger if it runs out of energy
        self.energy=energy
        
        #Rating of how well the snake performed during its life ~ used for genetic algorithm breeding
        self.fitness=0
        
        
        
    def draw(self):
        
        square_width=grid.square_width
        square_height=grid.square_height
        
        #Draw the shape of each component at the components position
        for comp in self.components:
            if comp.shape=='square':
                x1,y1=grid.x+comp.position[0]*square_width,grid.y+(comp.position[1]-1)*square_height
                x2,y2=int(comp.size),int(comp.size)
                pygame.draw.rect(win,comp.color,(x1,y1,x2,y2),0)
            elif comp.shape=='circle':
                x1,y1=grid.x+int(square_width*comp.position[0]+0.5*comp.size),grid.y+int(square_height*comp.position[1]-0.5*comp.size)
                pygame.draw.circle(win,comp.color,(x1,y1),int(0.5*comp.size))
    
    
    def snake_space(self):
        '''Returns a list of positions [(0,1),(0,2),(0,3),(1,3)...] that the
        snake currently inhabits'''
        return [comp.position for comp in self.components]
    
    
    def length(self):
        return len(self.components)        
            
            
        
class SnakeComponent(object):
    '''each square that makes up the snake will be a component
    perhaps I will add an option for using different shapes'''
    def __init__(self,size,position,color,shape='square'):
        
        #width of each square
        self.size=size
        
        #location of each square (starting at the origin)
        self.position=position
        
        #Choose whether the snake is made up of circles or squares
        self.shape=shape
        
        self.color=color
        
        
class SnakeFood(object):
    '''Food will appear at a random location that is not on the snake
    whenever the previous food has been eaten'''
    def __init__(self,size,position,color,shape='circle'):
        
        #use position to draw food on the board
        self.position=position
        
        #use true position for collisions
        self.true_position=(self.position[0]+grid.x,self.position[1]+grid.y)
        
        self.color=color
        self.shape=shape
        self.size=size
    
    def draw(self):
        
        #Width and height of box on grid
        square_width=grid.square_width
        square_height=grid.square_height
        
        if self.shape=='square':
            x1,y1=grid.x+self.position[0]*square_width,grid.y+self.position[1]*square_height
            pygame.draw.rect(win,self.color,(x1,y1,self.size,self.size),0)
        elif self.shape=='circle':
            x1,y1=grid.x+int(square_width*self.position[0]+0.5*self.size),grid.y+int(square_height*self.position[1]-0.5*self.size)
            pygame.draw.circle(win,self.color,(x1,y1),int(0.5*self.size))
        
        
class GridBoard(object):
    '''create a grid for the snake to move around on'''
    def __init__(self,rows,columns,width,height,position):
        self.width=width
        self.height=height
        self.rows=rows
        self.columns=columns
        
        #Grid position on the window
        self.x,self.y=position
        
        #Set grid line properties
        self.line_thickness=1
        self.border_thickness=3
        self.line_color=(100,100,100)
        self.border_color=(255,255,255)
        
        #width of a given square
        self.square_width=(self.width)/self.rows
        self.square_height=(self.height)/self.columns
        
    
    def draw(self):
        #ADD LINES AND BOARDER
        x_line_spacing=(self.width-1)/self.rows
        y_line_spacing=(self.height-1)/self.columns
        
        #Vertical Lines
        for i in range(1,self.columns):
            pygame.draw.line(win,self.line_color,(self.x+i*self.square_width,self.y),(self.x+i*self.square_width,self.y+self.height),self.line_thickness)
        
        #Horizontal Lines
        for j in range(1,self.rows):
            pygame.draw.line(win,self.line_color,(self.x,self.y+j*self.square_height),(self.x+self.width,self.y+j*self.square_height),self.line_thickness)

        
        #Border
        pygame.draw.rect(win,self.border_color,(self.x,self.y,self.width,self.height),self.border_thickness)

class ScoreBoard(object):
    def __init__(self,score,shape,**properties):
        self.score=score
        self.shape=shape
        self.high_score=1
        
        self.font=pygame.font.SysFont('tahoma',int(0.5*self.shape[1]),bold=True)
        
        self.snake_icon_loc=(int(0.35*(win_width-snake_icon.get_size()[0])),int(0.5*(self.shape[1]-snake_icon.get_size()[1])))
        
        for key,val in properties.items():
            setattr(self, k, v)
    
    def draw(self):
        
        if self.score>=self.high_score:
            self.font_color=(0,200,0)
        else:
            self.font_color=(200,200,200)
            
        #add a snake icon
        win.blit(snake_icon,self.snake_icon_loc)

        #Add text for the score
        score_text=self.font.render('Score: '+str(int(self.score)),1,self.font_color)
        win.blit(score_text,(10,int(0.5*(self.shape[1]-score_text.get_size()[1]))))
        
        #Add text for high score
        high_score_text=self.font.render('High Score: '+str(int(self.high_score)),1,self.font_color)
        win.blit(high_score_text,(win_width-10-high_score_text.get_size()[0],int(0.5*(self.shape[1]-high_score_text.get_size()[1]))))
        
        #text color for snake energy (start green for healthy and traverse to red)
        healthy=350
        health=min(severus.energy,healthy)
        energy_color=(255*(1-health/healthy),255*health/healthy,0)
        
        #Add text for snakes current energy
        snake_energy_text=self.font.render(str(int(severus.energy)),1,energy_color)
        win.blit(snake_energy_text,(int(self.snake_icon_loc[0]+snake_icon.get_size()[0]+5),int(0.5*(self.shape[1]-snake_energy_text.get_size()[1]))))

# =============================================================================
# INPUT VALUES FOR NEURAL NETWORK ARE OUTPUT VALUES FROM WHAT SNAKE SEES
# =============================================================================

def snakeVision(snake,food,obstruction_connections=True):
    '''
    Takes the snake of interest and current food as inputs returns an output
    of 20 values that the snake sees and a list of the locations of obstructions.
    
    The output will be fed as input to the neural net.  The list of obstructions
    will be used visualize what the snake sees as it moves (plot red spots on 
    obstruction locations).
    
    All distances are normalized to range between -1 and 1 where -1 represents
    a wall that is 30 blocks (the width of the screen) to the left or above the
    snakes head and 1 for 30 blocks to the right or below the snakes head
    
        note: this does not account for diagonal distances being root(2) times
        longer than horizontal or vertical distances... should only be of
        minor concern
    
    This in combination with the us of tanh as an activation function should
    assist in speeding up the training process
    
    If two observation points are connected by a series of obstructions it will
    be denoted by 1, if they are not connected -1
    
        i.e. Determine whether obstriction at right is connected to obstruction 
             at up-right by a chain of obstructions (i.e. right is wall and 
             upright is also wall)=1 or (i.e. right is tail not touching wall 
             and up right is wall)=-1
    
    
    outputs=[x dist from snakes head to food,
             y dist from snakes head to food,
             dist to nearest obstruction to the right,
             dist to nearest obstruction to the up-right,
             dist to nearest obstruction to the up,
             dist to nearest obstruction to the up-left,
             dist to nearest obstruction to the left,
             dist to nearest obstruction to the down-left,
             dist to nearest obstruction to the down,
             dist to nearest obstruction to the downright,
             is connected right & right-up,
             is connected up & right-up,
             is connected up & left-up,
             is connected left & left-up,
             is connected left & down-left,
             is connected down & down-left,
             is connected down & down-right,
             is connected right & down-right,
             direction snake is headed hoirzontally 1 for right, -1 for left, 0 for vertical
             direction snake is headed vertically 1 for down, -1 for up, 0 for horizontal
             ]
    '''
    
    outputs=[]
    
    #Add Food location x distance and y distance (consistently using final position - initial position)
    outputs.append(food.position[0]-snake.components[0].position[0])
    outputs.append(food.position[1]-snake.components[0].position[1])    
    
    #locate obstructions (snake's tail or wall) in 8 directions 
    #[right, up-right, up, up-left, left, down-left, down, down-right]
    obstructions=[]
    
    #Positions currently inhabited by snake body
    snake_space=set(tuple(snake.snake_space()[1:]))
    
    #Position of the snakes head
    x_naught,y_naught=snake.components[0].position[0],severus.components[0].position[1]
    
    #Helper dictionary for finding nearest obstruction in a given direction
    #Add the following (x,y) values when incrementing directions start right 
    #and go CCW (note: down is positive up is negative)
    direction_dict={'dir0':(1,0),'dir1':(1,-1),'dir2':(0,-1),'dir3':(-1,-1),
                    'dir4':(-1,0),'dir5':(-1,1),'dir6':(0,1),'dir7':(1,1)}
        
    #Find the nearest obstruction in direction ___ and note how far away it is
    #from the snakes head
    for direction in direction_dict:
        x,y=x_naught,y_naught
        dist=0
        while (x>=0 and x<=grid_columns-1) and (y>=0 and y<=grid_rows-1) and ((x,y) not in snake_space):
            x+=direction_dict[direction][0]
            y+=direction_dict[direction][1]
            dist+=1
        obstructions.append(tuple((x,y)))
        outputs.append(dist)
    
    #Determine whether obstriction at right is connected to obstruction at up-right
    #by a chain of obstructions (i.e. right is wall and upright is also wall)=1
    # or (i.e. right is tail not touching wal and up right is wall)=-1
        
    #add another copy of the obstruction to the right, to the end of the list
    obstructions.append(obstructions[0])
    
    if obstruction_connections:
        #check if each obstruction is connected to the one located CCW from it
        for idx,obstruction in enumerate(obstructions[:-1]):
            
            if (obstruction not in snake_space) and (obstructions[idx+1] not in snake_space):
                
                #if both obstructions are on the wall, then yes they are connected
                outputs.append(grid_rows) #will be normalized with other distances later
                
            elif (obstruction in snake_space) and (obstructions[idx+1] in snake_space):
                
                #if both obstructions are on the snake's body, then yes they are connected
                outputs.append(grid_rows)
                
            else:
                snake_is_touching_wall=False
                #If a part of the snake is adjacent to the wall, then yes they are connected
                for position in snake_space:
                    x,y=position
                    if (x<1 or x>=grid_columns-1) or not (y<2 or y>grid_rows-1):
                        snake_is_touching_wall=True
                
                if snake_is_touching_wall:
                    outputs.append(grid_rows)
                else:
                    #Snake is not touching the wall
                    outputs.append(-grid_rows)
    
    #Lastly lets tell the snake what direction it is currently headed:
    #horizontal: (-1,0) --> -1 | (1,0) --> 1  | (0,+/- 1) --> 0
    #vertical: (-1,0) --> 0 | (1,0) --> 0  | (0,+/- 1) --> +/- 1  
    outputs.append(snake.direction[0]*grid_rows)
    outputs.append(snake.direction[1]*grid_rows)
        
    
    #Normalize ouputs
    outputs=[output/grid_rows for output in outputs]
    
    return (outputs,obstructions)

def drawObstructions(obstructions):
    '''
    Obstructions are given from snake vision, they are (x,y) pairs of locations
    that will cause the snake to die if touched
    
    drawObstructions([(1,2),(7,9),(30,5),...])
    will blit a red square anywhere that is hazardous to the snake
    '''
    
    #Plot a red square slightly larger than the grid square size at each location
    marker_size=0.5
    square_width,square_height=marker_size*grid.square_width,marker_size*grid.square_height
    
    for obstruction in obstructions:
        color=(255,0,0)

        x,y=obstruction
        x1,y1=grid.x+x*grid.square_width,grid.y+y*grid.square_height
        
        if x==grid_columns:
            x1-=grid.square_width-square_width
        elif x==-1:
            x1+=grid.square_width
        elif y==grid_rows:
            y1-=square_height
        elif y==-1:
            y1+=grid.square_height
        else:
            x1+=int(0.5*(grid.square_width-square_width))
            y1-=int(0.5*(2*grid.square_width-square_height))
            color=(255,255,255)
            
        pygame.draw.rect(win,color,(x1,y1,square_width,square_height),0)
        
# =============================================================================
# REDRAW GAME WINDOW     
# =============================================================================

def redrawGameWindow():
    
    pygame.draw.rect(win,(0,0,0),(0,0,win_width,win_height))
    
    grid.draw()
    severus.draw()
    food.draw()
    header.draw()
    
    drawObstructions(obstructions)
    
    pygame.display.update()

# =============================================================================
# INITIAL CONDITIONS FOLLOWED BY RUN LOOP
# =============================================================================

def main():
    #objects
    global grid, win, severus, food, header
    
    #dimensions
    global grid_rows,grid_columns, win_width, win_height, food_energy
    
    #flags and values
    global colors, game_on, snake_icon, obstructions, snake_output
    
    
    #SET INITIAL CONDITIONS
    clock=pygame.time.Clock()
    win_width=500
    win_height=win_width+50
    win=pygame.display.set_mode((win_width,win_height))
    
    
    #Size of grid for snake to move on
    grid_columns,grid_rows=30,30
    
    
    #Range of colors to randomly choose from for snake food
    color_dict={'red':(255,0,0),
            'orange':(255,127,0),
            'yellow':(255,255,0),
            'green':(0,255,0),
            'blue':(0,0,255),
            'indigo':(75,0,130),
            'violet':(148,0,211)}
    colors=['red','orange','yellow','green','blue','indigo','violet']
    
    
    #Energy that each food contains
    food_energy=300
    
    
    #flag for whether the snake is alive
    game_on=True


    #CREATE INITIAL OBJECTS
    #Square grid the same width as the window
    grid=GridBoard(grid_columns,grid_rows,win_width,win_width,(0,win_height-win_width))
    
    
    #Snake
    severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)
    
    
    #Score Board Snake Icon Resized to fit scoreboard
    snake_icon=pygame.image.load('./images/snake-image-alpha-removed.png')
    snake_icon_ratio=1280/960
    snake_icon=pygame.transform.scale(snake_icon,(int(snake_icon_ratio*0.75*(win_height-win_width)),int(0.75*(win_height-win_width))))
    
    
    #Score Board
    header=ScoreBoard(severus.length(),(win_width,win_height-win_width))
    

    #Add food to the map in a location that the snake does not inhabit
    food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
    while food_loc in severus.snake_space():
        food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
    food=SnakeFood(int(grid.square_width),food_loc,color_dict[np.random.choice(colors)],shape=severus.components[0].shape)

    
    #run loop
    run=True
    while run:
        
        snake_output,obstructions=snakeVision(severus,food)
        
        #Set the speed the game runs at playing: (50,20) | training (0,comment out)
        pygame.time.delay(50)
        clock.tick(10)
        
        #Every time step, severus loses one energy [kcal]
        severus.energy-=1
        
        #get list of all events that happen i.e. keyboard, mouse, ...
        for event in pygame.event.get():
            #Check if the red X was clicked
            if event.type==pygame.QUIT:
                run=False
        
        #keep track of where the snakes tail is before movement incase it eats food
        severus.tail=severus.components[-1]
        
        keys=pygame.key.get_pressed()
        #TRACK INPUTS FROM MOUSE/KEYBOARD HERE
        if (keys[pygame.K_LEFT] and severus.direction!=(1,0)) or severus.direction==(-1,0):
            #Only allow a left turn if the snake is not going right
            
            #Update the snakes tail components position to be to the left of the snakes head This will create the illusion of the snake progressing forward
            severus.components[-1].position=(severus.components[0].position[0]-1,severus.components[0].position[1])
            #Move the tail component to the head position of the snake
            severus.components=[severus.components.pop()]+severus.components
            #Change the direction of the snake to left
            severus.direction=(-1,0)
            
            
        if (keys[pygame.K_RIGHT] and severus.direction!=(-1,0)) or severus.direction==(1,0):
            severus.components[-1].position=(severus.components[0].position[0]+1,severus.components[0].position[1])
            severus.components=[severus.components.pop()]+severus.components
            severus.direction=(1,0)
            
        if (keys[pygame.K_UP] and severus.direction!=(0,1)) or severus.direction==(0,-1):
            severus.components[-1].position=(severus.components[0].position[0],severus.components[0].position[1]-1)
            severus.components=[severus.components.pop()]+severus.components
            severus.direction=(0,-1)
            
        if (keys[pygame.K_DOWN] and severus.direction!=(0,-1)) or severus.direction==(0,1):
            severus.components[-1].position=(severus.components[0].position[0],severus.components[0].position[1]+1)
            severus.components=[severus.components.pop()]+severus.components
            severus.direction=(0,1)

            
        #If the snake finds food it will grow by lenght 1
        if severus.components[0].position==food.position:
            #elongate snake with color of food
            severus.components.append(SnakeComponent(grid.square_width,severus.tail.position,food.color,shape=food.shape))
            
            #update the score
            header.score=severus.length()
            
            if header.score>=header.high_score:
                header.high_score=header.score
            
            #randomly set new food location that is not on the snake
            food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
            while food_loc in severus.snake_space():
                food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
            food.position=food_loc
            
            #Increase snakes energy after eating food
            severus.energy+=food_energy
            
            #Pygame snakes cannot store more than 999 kilocalories, excess is not metabolized
            if severus.energy>999:
                severus.energy=999         
        else:
            #If the snake bites its tail or wanders into the hunting zone the snake becomes injured
            #note if snake does not move off of food in one frame it will register as biting its own tail
            x,y=severus.components[0].position[0],severus.components[0].position[1]
            if (x<0 or x>=grid_columns) or (y<1 or y>grid_rows) or ((x,y) in severus.snake_space()[1:]):
                #game over because of biting tail or out of bounds
                game_on=False
                
            #If the snake tries to go out of bounds reset the head to the tail
            if (x<0 or x>=grid_columns) or (y<1 or y>grid_rows):
                severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)
        
        
        #The snake starved before finding food
        if severus.energy<=0:
            game_on=False
            
            
        #If snake died of starvation, bit its tail or hit a wall
        if not game_on:
            print('snake injured at ('+str(x)+','+str(y)+')')
            if header.high_score<=severus.length():
                header.high_score=severus.length()
            
            severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)

            header.score=severus.length()
            
            #run=False: kill game | game_on=True: reset snake
            #run=False
            game_on=True
                
        
        #REDRAW GAME WINDOW
        redrawGameWindow()
    
    
    pygame.quit()
    

def evalGenomes(population, generations, fitness_threshold=200, mutation_rate=0.03, mutation_range=[-2,2], nn_shape=[20,12,8,4], activation_functions=['tanh','tanh','tanh','softmax'], initial_config=False, watch=False):
    '''
    population: the number of snakes in each generation
    generations: the number of generations you wish to run the evolution process for
    
    mutation rate: probability of a gene mutating
    mutation_range: the min and max possible mutated value
    nn_shape: the shape of the neural net: input layer, hidden 1, hidden 2, ..., output
    activation_functions: the function that will be used at layer1, layer2, ..., output
    
    initial_config: If False, the neural network will initiate with random weights on generation 1
                    If initial_config='configuration_file_name.pkl' then neural net will use
                    the weights from the pkl file, thus starting from a partially evolved state
    
    '''
    
    # =============================================================================
    # MAIN LOOP
    # =============================================================================
    '''From here until the run loop is simply initializing game objects such as
    the snake population, the board, food, etc.  
    '''
    
    #objects
    global grid, win, severus, food, header
    
    #dimensions
    global grid_rows,grid_columns, win_width, win_height, food_energy
    
    #flags and values
    global colors, game_on, snake_icon, obstructions, snake_output, gen
    
    
    
    
    
    
    gen=0
    
    #SET INITIAL CONDITIONS
    if watch:
        clock=pygame.time.Clock()
    win_width=500
    win_height=win_width+50
    if watch:
        win=pygame.display.set_mode((win_width,win_height))
    
    
    #Size of grid for snake to move on
    grid_columns,grid_rows=15,15
    
    
    #Range of colors to randomly choose from for snake food
    color_dict={'red':(255,0,0),
            'orange':(255,127,0),
            'yellow':(255,255,0),
            'green':(0,255,0),
            'blue':(0,0,255),
            'indigo':(75,0,130),
            'violet':(148,0,211)}
    
    colorful=True
    if colorful:
        colors=['red','orange','yellow','green','blue','indigo','violet']
    else:
        colors=['green']
    
    
    #Energy that each food contains
    food_energy=300
    
    
    #flag for whether the snake is alive
    game_on=True


    #CREATE INITIAL OBJECTS
    #Square grid the same width as the window
    grid=GridBoard(grid_columns,grid_rows,win_width,win_width,(0,win_height-win_width))
    
    
    #Snake
    severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)
    
    
    #Score Board Snake Icon Resized to fit scoreboard
    snake_icon=pygame.image.load('./images/snake-image-alpha-removed.png')
    snake_icon_ratio=1280/960
    snake_icon=pygame.transform.scale(snake_icon,(int(snake_icon_ratio*0.75*(win_height-win_width)),int(0.75*(win_height-win_width))))
    
    
    #Score Board
    header=ScoreBoard(severus.length(),(win_width,win_height-win_width))
    

    #Add food to the map in a location that the snake does not inhabit
    food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
    while food_loc in severus.snake_space():
        food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
    food=SnakeFood(int(grid.square_width),food_loc,color_dict[np.random.choice(colors)],shape=severus.components[0].shape)

    

    # =============================================================================
    # CREATE FIRST POPULATION OF SNAKES AND NEURAL NETWORKS
    # =============================================================================
    #record the history of the performance of each generation of snakes
    history={'best' : [],
             'average' : [],
             'std' : [],
             'run_time' : []
             }
    
    nets = []
    snakes = []
    fitness = [0]*population
    
    #if no initial_configuration file is given, randomly generate neural net weights
    if not initial_config:
        for i in range(population):
            snakes.append(Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy))
            
            #weights for connections between nodes
            #conn_weights=[scale(np.random.rand(20,12)),scale(np.random.rand(12,8)),scale(np.random.rand(8,4))]
            conn_weights=[scale(np.random.rand(nn_shape[idx],nn_shape[idx+1])) for idx in range(len(nn_shape)-1)]
            #bias for each node
            #bias_weights=[scale(np.random.rand(12,)), scale(np.random.rand(8,)), scale(np.random.rand(4,))]
            bias_weights=[scale(np.random.rand(nn_shape[idx+1],)) for idx in range(len(nn_shape)-1)]
            
            #create neural net with given weights and activation functions
            nets.append(make_nets(conn_weights,bias_weights,activation_functions))
    else:
        #build population of snakes
        for i in range(population):
            snakes.append(Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy))
        
        #load top 50 nerual nets from previous session
        net_files=glob.glob('ga_snake_history/checkpoint_weights/*.h5')
        net_files=[i.split('\\')[-1] for i in net_files]
        
        nets=[]
        #Manually compile the top 50 neural nets from previous session
        for file in net_files:
            print()
            print('Manually loading, flattening, and rebuilding neural net',file,'from checkpoint.')
            net=keras.models.load_model('./ga_snake_history/checkpoint_weights/'+file)
            flattened_net=flatten_net(net)
            connection_weights,bias_weights=rebuild_net(flattened_net,nn_shape)
            nets.append(make_nets(connection_weights,bias_weights,activation_functions))
        
        #Reload the latest history
        with open('./ga_snake_history/history.pkl', 'rb') as file:
            history = pickle.load(file)
            
        #if the population is larger than 50, expand on the loaded neural nets to fill the population
        for i in range(population-len(nets)):
            nets.append(np.random.choice(nets))
        
        #mutate the nets to add diversity
        nets=mutate(nets)
        
        print('nets')
        print(len(nets))


            
    #Decide how much the snake should be rewarded for each positive/negative action
    reward_food = 2
    reward_move = 0.01
    reward_hit_wall = - 1
    
    for gen in range(generations):
        t_start=time.time()
        gen+=1

        #run loop
        snake_count=0
        for index,severus in enumerate(snakes):
            
            #Progress bar
            if snake_count%25==0:
                empty=' '*50
                full='|'*50
                progress=float(snake_count)/float(population)
                print('|'+full[:int(progress*50)]+empty[:int((1-progress)*50)]+'|')
            snake_count+=1

            run=True                
            while run:
            
                #Set the speed the game runs at playing: (50,20) | training (0,comment out)
                #pygame.time.delay(0)
                #clock.tick(100)
                
                #Every time step, severus loses one energy [kcal]
                severus.energy-=1
                
                #get list of all events that happen i.e. keyboard, mouse, ...
                for event in pygame.event.get():
                    #Check if the red X was clicked
                    if event.type==pygame.QUIT:
                        run=False
                
                #keep track of where the snakes tail is before movement incase it eats food
                severus.tail=severus.components[-1]
                
                
                # =============================================================================
                # CONTROL SNAKE USING NEURAL NET      
                # =============================================================================
                #Increase the snakes fitness for each frame it has lived 
                severus.fitness += reward_move
                
                #Output the snake vision to the neural net
                snake_output,obstructions = snakeVision(severus,food)
                
                
                snake_output=np.reshape(np.array(snake_output),(1,-1))
                
                #Ask neural net what snake should do based on snake's vision
                nn_output = nets[index].predict(snake_output)
                                
                #Perform action suggested by nn_output
                snake_actions={0:'RIGHT',1:'UP',2:'LEFT',3:'DOWN',4:'NONE'}
                
                #OUTPUT FROM NEURAL NET (NN_OUTPUT) DRIVES THE SNAKE
                if (snake_actions[np.argmax(nn_output)]=='LEFT' and severus.direction!=(1,0)) or severus.direction==(-1,0):
                    #Only allow a left turn if the snake is not going right
                    
                    #Update the snakes tail components position to be to the left of the snakes head This will create the illusion of the snake progressing forward
                    severus.components[-1].position=(severus.components[0].position[0]-1,severus.components[0].position[1])
                    #Move the tail component to the head position of the snake
                    severus.components=[severus.components.pop()]+severus.components
                    #Change the direction of the snake to left
                    severus.direction=(-1,0)
                    
                    
                if (snake_actions[np.argmax(nn_output)]=='RIGHT' and severus.direction!=(-1,0)) or severus.direction==(1,0):
                    severus.components[-1].position=(severus.components[0].position[0]+1,severus.components[0].position[1])
                    severus.components=[severus.components.pop()]+severus.components
                    severus.direction=(1,0)
                    
                if (snake_actions[np.argmax(nn_output)]=='UP' and severus.direction!=(0,1)) or severus.direction==(0,-1):
                    severus.components[-1].position=(severus.components[0].position[0],severus.components[0].position[1]-1)
                    severus.components=[severus.components.pop()]+severus.components
                    severus.direction=(0,-1)
                    
                if (snake_actions[np.argmax(nn_output)]=='DOWN' and severus.direction!=(0,-1)) or severus.direction==(0,1):
                    severus.components[-1].position=(severus.components[0].position[0],severus.components[0].position[1]+1)
                    severus.components=[severus.components.pop()]+severus.components
                    severus.direction=(0,1)
        
                    
                #If the snake finds food it will grow by lenght 1
                if severus.components[0].position==food.position:
                    #elongate snake with color of food
                    severus.components.append(SnakeComponent(grid.square_width,severus.tail.position,food.color,shape=food.shape))
                    
                    #update the score
                    header.score=severus.length()
                    
                    if header.score>=header.high_score:
                        header.high_score=header.score
                    
                    #generate new food at a location not on the snake
                    food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
                    while food_loc in severus.snake_space():
                        food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
                    food=SnakeFood(int(grid.square_width),food_loc,color_dict[np.random.choice(colors)])
                    
                    #Increase snakes energy after eating food
                    severus.energy+=food_energy
                    
                    #Increase the snakes fitness for finding food
                    severus.fitness += reward_food
                    
                    #Pygame snakes cannot store more than 999 kilocalories, excess is not metabolized
                    if severus.energy>999:
                        severus.energy=999         
                else:
                    #If the snake bites its tail or wanders into the hunting zone the snake becomes injured
                    #note if snake does not move off of food in one frame it will register as biting its own tail
                    x,y=severus.components[0].position[0],severus.components[0].position[1]
                    if (x<0 or x>=grid_columns) or (y<1 or y>grid_rows) or ((x,y) in severus.snake_space()[1:]):
                        #game over because of biting tail or out of bounds
                        severus.fitness += reward_hit_wall
                        game_on=False
                        
                    #If the snake tries to go out of bounds reset the head to the tail
                    #if (x<0 or x>=grid_columns) or (y<1 or y>grid_rows):
                    #    severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)
                
                
                #The snake starved before finding food
                if severus.energy<=0:
                    game_on=False
                    
                    
                #If snake died of starvation, bit its tail or hit a wall
                if not game_on:
                    #print('snake injured at ('+str(x)+','+str(y)+')')
                    if header.high_score<=severus.length():
                        header.high_score=severus.length()
                    
                    #record how fit the snake was
                    fitness[index]=severus.fitness  
                    
                    #reset snake
                    severus=Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy)
                    
                    #reset food
                    food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
                    while food_loc in severus.snake_space():
                        food_loc=tuple((np.random.randint(1,grid_columns),np.random.randint(1,grid_rows)))
                    food=SnakeFood(int(grid.square_width),food_loc,color_dict[np.random.choice(colors)],shape=severus.components[0].shape)

                    
                    #update score
                    header.score=severus.length()
                
                    #run=False: kill game | game_on=True: reset snake
                    #run=False
                    game_on=True
                    
                    #Break from while loop and continue with the next snake
                    break
    
    
                #REDRAW GAME WINDOW
                if watch:
                    redrawGameWindow()
                
        # =============================================================================
        # SELECT THE MOST FIT PARENTS TO SURVIVE AND BREED
        # =============================================================================
        #Agent[0]=(net[0],fitness[0])
        agents=selection(nets,fitness,survival_fraction=0.2)
        
        # =============================================================================
        # PERFORM CROSSOVER TO MAKE CHILD NEURAL NETS FROM TOP PERFORMING PARENTS
        # =============================================================================
        nets=[agent[0] for agent in agents]
        nets.extend(crossover(agents,nn_shape,activation_functions))
        
        # =============================================================================
        # SAVE THE BEST FIT PARENT TO MONITOR HOW THE POPULATION GREW FROM GENERATION TO GENERATION
        # =============================================================================
        
        #Save the ost recent copy of the history dictionary
        with open('./ga_snake_history/history.pkl','wb') as file:
            pickle.dump(history, file, protocol=pickle.HIGHEST_PROTOCOL)

        
        #Save the most recent copy of the top 50 snakes
        save_count=0
        for net in nets:
            #net.save_weights('./ga_snake_history/checkpoint_weights/'+str(save_count)+'_weights')
            net.save('./ga_snake_history/checkpoint_weights/'+str(save_count)+'_weights.h5')
            save_count+=1
            if save_count==50:
                break
            

        # =============================================================================
        # IF A GENOME (NEURAL NET) WAS GOOD ENOUGH TO MEET THE FINAL REQUIREMENT THEN BREAK      
        # =============================================================================
        history['best'].append(np.max(fitness))
        history['average'].append(np.mean(fitness))
        history['std'].append(np.std(fitness))
        history['run_time'].append(time.time()-t_start)
        
        reporter(history)
        
        
        #Save a copy of the best neural network from each generation
        #nets[0].save_weights('./ga_snake_history/best/'+str(gen)+'_best')
        nets[0].save('./ga_snake_history/best/'+str(len(history['best'])+1)+'_best.h5')
        
        # =============================================================================
        # IF A SATISFACTORY SNAKE EXISTS, BREAK (i.e. snake can reach a score of 200)
        # =============================================================================
        if max(fitness)>fitness_threshold:
            print('A super snake has been born.')
            break
        
        # =============================================================================
        # ADD RANDOM MUTATIONS
        # =============================================================================
        nets=mutate(nets)
        
        #reset snake population and fitness values for next round
        snakes = []
        fitness = [0]*population
        
        for i in range(population):
            snakes.append(Snake((1,0),SnakeComponent(int(grid.square_width),(int(0.5*grid_columns),int(0.5*grid_rows)),(0,255,0),shape='circle'),food_energy))

def scale(arr,minimum=-2,maximum=2):
    ''' Scale a np.random.rand array to range from minimum to maximum'''
    return (arr-0.5)*(maximum-minimum)

def reporter(history, plot=True, savefile='./ga_snake_history/'):
    '''Prints statistics about the most recent population to monitor growth'''
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('~~~~~~~~~~~~~~GENERATION: '+str(len(history['best'])+1)+'~~~~~~~~~~~~~~~~~~')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')

    print('Best:',str(round(history['best'][-1],2)))
    print('Average:',str(round(history['average'][-1],2)))
    print('Standard Deviation:',str(round(history['std'][-1],2)))
    print('Run Time:',str(round(history['run_time'][-1],2)))
    
    if plot:
        generations=np.linspace(1,len(history['best']),len(history['best']))
        best=history['best']
        average=history['average']
        std=history['std']
        
        average_std_over=[a+s for (a,s) in zip(average,std)]
        average_std_under=[a-s for (a,s) in zip(average,std)]
        
        plt.plot(generations,best,'r-',label='Best',lw=2)
        plt.plot(generations,average,'b-',label='Average',lw=2)
        plt.plot(generations,average_std_over,'g--',label='+1 STD')
        plt.plot(generations,average_std_under,'g--',label='-1 STD')
        plt.savefig(savefile+'progress_plot.png')

            
def mutate(nets, mutation_range=[-2,2], mutation_rate=0.03, nn_shape=[20,12,8,4], activation_functions=['tanh','tanh','tanh','softmax']):
    mutated_nets=[]
    
    for net in nets:
        #Flatten neural network to 1D list
        net = flatten_net(net)
        
        #use a list of booleans to denote whether a gene will be mutated
        mutate = np.random.rand(len(net)) <= mutation_rate
        for idx,result in enumerate(mutate):
            if result:
                net[idx]=scale(np.random.rand(),minimum=mutation_range[0],maximum=mutation_range[1])
        
        #Rebuild the neural_network model from the flattened child net
        connection_weights,bias_weights = rebuild_net(net,nn_shape)
        mutated_net = make_nets(connection_weights,bias_weights,activation_functions)
        
        mutated_nets.append(mutated_net)
    
    return mutated_nets


def make_nets(connection_weights,bias_weights,activation_functions):
    ''' Each layer after the initial input layer of a densly connected FFNN 
    will have connection weights in the form of numpy array with the shape of 
    
    connection_weight_shape=(number_of_previous_layers_nodes,number_of_current_layers_nodes)
    
    there will also be one bias weight for each node in a layer with the shape of
    
    bias_weight_shape=(number_of_nodes_in_current_layer, )

    A densly connected NN will be made given weights for each connection and bias
    
    activation_functions should be given as a list where acceptable values are:
        'sigmoid','tanh','relu','softmax'
        
    Provide one array of connection_weights, one of bias_weights, and one activation
    function for each layer beyond the initial layer:
        
        i.e. for two hidden layers with 20 inputs, 12 hidden nodes, 8 hidden nodes, 4 output nodes:
            
            make_nets([np.random.rand(20,12),np.random.rand(12,8),np.random.rand(8,4)],
                       [np.random.rand(12,), np.random.rand(8,), np.random.rand(4,)],
                       ['tanh','tanh','softmax'])
            
            note, this is only for the first guess at the neural net weights.  After which,
            use the genetic algorithm to choose weights instead of using np.random.rand
    '''
    
    connections=[conn for conn in connection_weights]
    biases=[bias for bias in bias_weights]
    activations=[fcn for fcn in activation_functions]
    
    model=keras.models.Sequential([keras.layers.Input(shape=(connections[0].shape[0],))])
    
    for (c,b,a) in zip(connections,biases,activations):
        model.add(keras.layers.Dense(c.shape[1],weights=[c,b],activation=a))
    
    return model

def selection(nets,fitness, survival_fraction=0.2):
    '''Returns a zipped list of the top {survival_fraction} percent of neural
    networks based on their fitness'''
    
    agents=zip(nets,fitness)
    agents=sorted(agents, key=lambda agent: agent[1], reverse=True)
    
    #Return the top 20% of most fit agents to move on and breed    
    return agents[:int(survival_fraction*len(agents))]

def crossover(agents,nn_shape,activation_functions):
    child_nets=[]
    
    for i in range(int(population-len(agents))):
        #create one child each loop, until len(nets)+len(child_nets)=population
        
        #Randomly select two parents
        agent_index_1 = np.random.randint(len(agents))
        agent_index_2 = np.random.randint(len(agents))
        
        #Make sure the parents are not identical
        while agent_index_1 == agent_index_2:
            agent_index_2 = np.random.randint(len(agents))
        
        #Flatten parents neural_net weights (both connection and bias weights) to a 1D list for crossover
        parent_1 = flatten_net(agents[agent_index_1][0])
        parent_2 = flatten_net(agents[agent_index_2][0])
        
        #Fitness of each parent
        fitness_1 = agents[agent_index_1][1]
        fitness_2 = agents[agent_index_2][1]
        
        #Randomly select which parent the child gets its gene on while giving
        #a higher probability to the more fit parents genes
        try:
            probability_threshold = fitness_1 / (fitness_2 + fitness_1)
        except:
            #in the case that fitness_1+fitness_2=0
            probability_threshold = 0.5
        
        #If p1_genes is true, the child gets that gene from parent 1
        p1_genes = np.random.rand(len(parent_1)) <= probability_threshold
        
        child=np.array([0]*len(parent_1))
        child_gene_index=0
        for p1,p2,p1_gene in zip(parent_1,parent_2,p1_genes):
            if p1_gene:
                child[child_gene_index]=p1
            else:
                child[child_gene_index]=p2
            child_gene_index+=1
            
        
        #Rebuild the neural_network model from the flattened child net
        connection_weights, bias_weights = rebuild_net(child, nn_shape)
        child_net = make_nets(connection_weights, bias_weights, activation_functions)
        
        child_nets.append(child_net)
        
    return child_nets

def flatten_net(net):
    #Extract Numpy arrays of connection and bias weights from model
    layers=[layer.numpy() for layer in net.weights]
    
    #Convert each array to 1 dimension along the x-axis
    flat_layers=[np.reshape(layer,(-1,1)) for layer in layers]
    
    #Collect all connection andn bias weights into a list
    flattened_net=[]
    for layer in flat_layers:
        flattened_net.extend(layer)
        
    #convert all values to floats
    flattened_net=[float(weight) for weight in flattened_net]
        
    return flattened_net

def rebuild_net(flattened_net,nn_shape):
    '''
    Takes a list of the connection and bias weights in 1D form:
        List of all node connection weights for hidden layer 1
        List of all bias weights for hidden layer 1
        List of all node connedction weights for hidden layer 2
        ...
        List of all node connection weights for output layer
        List of all bias weights for output layer
    
    Restructures the flattened_net into arrays where each node layer
    has a 1D bias array and each connection layer has a 2D connection weight array
    
    the shape of each bias array is (number_of_nodes_in_layer,1)
    the shape of each connection weight array is (number_of_nodes_in_previous_layer,number_of_nodes_in_current_layer)
    
    
    i.e.: for a model with 3 input, 1 hidden layer of 2 nodes, and 1 output:
        
        connection_weights layer 1: 0.5, 0.7, -0.3, 0.4, 0.8, -0.6
        bias_weights layer 1: 0, 0
        connection_weights output layers: 0.8, -0.4
        bias_weights output layer: 0
        
        
    In : rebuild_net([0.5,0.7,-0.3,0.4,0.8,-0.6,0,0,0.8,-0.4,0])
    
    Out: ( list of connection weight numpy arrays, list of bias weight numpy arrays )
         ( [[[0.5,0.7,-0.3],[0.4,0.8,-0.6]], [0.8,-0.4]], [[0,0], [0]] )
    '''
    
    connection_weights=[]
    bias_weights=[]
    
    start_idx=0
    for idx in range(1,len(nn_shape)):
        #Add a reshaped layer to the connection_weights list
        end_idx=int(start_idx+nn_shape[idx-1]*nn_shape[idx])
        connection_weights.append(np.reshape(flattened_net[start_idx:end_idx],(nn_shape[idx-1], nn_shape[idx])))
        start_idx=end_idx
        
        #Add reshaped bias weights
        end_idx=int(start_idx+nn_shape[idx])
        bias_weights.append(np.reshape(flattened_net[start_idx:end_idx],(nn_shape[idx],)))
        start_idx=end_idx
        
    return (connection_weights,bias_weights)


if __name__ == '__main__':
    population=500
    generations=20
    fitness_threshold=200
    
    mutation_rate=0.1
    mutation_range=[-2,2]
    
    nn_shape=[20,12,8,4]
    activation_functions=['tanh','tanh','tanh','softmax']
    
    #Set initial config if continuing from partially trained neural nets
    initial_config=True
    
    #set watch to True if you want to watch each generation of snake
    watch=False
    
    evalGenomes(population, generations, fitness_threshold=fitness_threshold, 
                 mutation_rate=mutation_rate, mutation_range=mutation_range, 
                 nn_shape=nn_shape, activation_functions=activation_functions, 
                 initial_config=initial_config, watch=watch)
    
    pygame.quit()
    
    #main()
    
    
        
        
        
        
        
        
        
        