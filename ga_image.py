# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 23:58:35 2020

@author: Logan Rowe

I will attempt to recreate an image using the genetic algorithm

To keep things simple I will limit the image to three shades: white, gray, black
"""

import random
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class Agent(object):
    def __init__(self,length):
        
        #Initialize flattened image guess as [0,0,0,1,0,1,1,0,.....]
        self.arr=np.random.randint(0,2,length)
        
        #Prior to fit use -1 to denote not fitted
        self.fitness=-1
        
    def __str__(self):
        return '\nFitness: '+str(self.fitness)
    

in_img=None
in_img_size=None
population=20
generations=1000
mutation_rate=0.03

values=[0,1]

def ga():
    '''
    The genetic algorithm (ga) run function:
        
        creates a population of random agents
        
        checks each agent in the population ot see how well it fits the desired goal
        
        Picks the best agents to be parents and breed
        
        Creates new agents using cross over
        
        Adds in a few (3%) mutations to add variance that may not be large enough in the initial population
    '''
    global generations, in_img_size, in_img, population
    
    #each agent is a random string
    agents = init_agents(population, in_img_size)
    
    for generation in range(generations):
        print('Generation: '+str(generation))
        
        plt.imsave(str(generation)+'.png',np.reshape(agents[0].arr,(50,50)))
        
        agents=fitness(agents)
        agents=selection(agents)
        agents=crossover(agents)
        agents=mutation(agents,mutation_rate)
        
        if any(agent.fitness==1.0 for agent in agents):
            print('Threshold met!')
            break

def init_agents(population,img_size):
    '''generates a number of agents equal to the population'''
    return [Agent(in_img_size) for _ in range(population)]

def fitness(agents):
    for agent in agents:
        score=0
        for idx in range(in_img_size):
            if agent.arr[idx]==in_img[idx]:
                score+=1
        agent.fitness=score/len(agent.arr)
            
    return agents

def selection(agents):
    agents=sorted(agents, key=lambda agent: agent.fitness, reverse=True)
    
    #Show the best fit agent of the current population
    #plt.imshow(np.reshape(agents[0].arr,(50,50)))
    
    #Take the top 20% of agents (4 agents) to move on
    agents=agents[:int(0.2*len(agents))]
    
    return agents

def crossover(agents):
    offspring=[]
    
    for i in range(int(0.5*(population-len(agents)))):
        
        #There is potential for picking the same parent but thats ok for now
        parent1 = random.choice(agents)
        parent2 = random.choice(agents)
        
        #Create two random children
        child1=Agent(in_img_size)
        child2=Agent(in_img_size)
        
        #Choose a random location to make the crossover
        split=random.randint(0,in_img_size)
        
        #Construct children according to their parents dna
        child1.arr=np.array(list(parent1.arr[0:split])+list(parent2.arr[split:in_img_size]))
        child2.arr=np.array(list(parent2.arr[0:split])+list(parent1.arr[split:in_img_size]))

        offspring.append(child1)
        offspring.append(child2)
        
    agents.extend(offspring)
    
    return agents

def mutation(agents,mutation_rate):
    '''For each letter in the string there is a chance of it mutating (0.03)
    If the letter mutates, swap that index with a random letter'''
    
    for agent in agents:
        for idx in range(len(agent.arr)):
            if random.uniform(0.0, 1.0) <= mutation_rate: 
                agent.arr=np.array(list(agent.arr[:idx])+[random.choice(values)]+list(agent.arr[idx+1:in_img_size]))
    
    return agents

def black_and_white(img):
    arr=img[:,:,0]+img[:,:,1]+img[:,:,2]
    arr=arr/3
    
    threshold=np.mean(arr)
    
    arr[arr<threshold]=int(0)
    arr[arr>=threshold]=int(1)
    
    return arr.astype(int)

if __name__=='__main__':
    #Load image to be recreated by genetic algorithm
    in_img=np.array(Image.open('simplified-logo-small.png'))
    
    #Convert image to black and white to limit the potential values for each pixel
    in_img=black_and_white(in_img)
    
    #Convert image to a 1-d array so that the genetic algorithm can treat it like a list
    in_img=np.reshape(in_img,(1,-1))[0]
    
    in_img_size=len(in_img)
    ga()