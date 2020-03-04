# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:34:58 2020

@author: Logan Rowe
"""

import snake_game

'''
death_count=0
while death_count<-1:
    snake_game.main()
    if snake_game.game_on!=True:
        death_count+=1
    print(death_count)
    

snake_game.main()
death_count+=1
snake_game.main()
death_count+=1
print(death_count)
'''

def eval_genomes(genomes, config):
    '''Run calls this fcn which iterates through steps in the environment
    to evaluate each genome'''
    for genome_id, genome in genomes:
        
        #ob= observation variable first input for our neural network
        #ac= action variable 
        
        #
        
        
        genome.fitness = 4.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = net.activate(xi)
            genome.fitness -= (output[0] - xo[0]) ** 2


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    
    # Create the population, which is the top-level object for a NEAT run.
    #This creates the variable genomes
    p = neat.Population(config)
    
    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)
    
    

        
