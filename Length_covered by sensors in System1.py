# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 09:52:24 2022

@author: a1643537
"""


# Identify the minimum number of sensor to cover the entire network
from deap import base
from deap import creator
from deap import tools
import numpy as np
import pandas as pd
import copy
import random
from functools import partial
random.seed(42)

# Import data from Topological solution, which is saved under the pread sheet "DownstreamDependent"
fileName='U:\phd_program_ninh\Data and code\paper1\System1_network.xlsx'

DownStreamDependentDB=pd.read_excel(fileName,sheet_name='DownstreamDependent')
DownStreamDependentDB

linkDownStreamDependentDB=pd.read_excel(fileName,sheet_name='DownstreamDependent_Link')
linkDownStreamDependentDB

NodeDB=pd.read_excel(fileName,sheet_name='Node')
NodeDB

LinkDB=pd.read_excel(fileName,sheet_name='Link')
LinkDB

ManholeID=pd.read_excel(fileName,sheet_name='ManholeLocation')
ManholeID

#Find all covered nodes
coveredNodesbyManhole=pd.Series()

coveredNodesbyManhole

DownStreamDependentDB.shape[1] 


for i in range (DownStreamDependentDB.shape[1]):
    tmp=DownStreamDependentDB.iloc[:,i].dropna()
    coveredNodesbyManhole=pd.concat([coveredNodesbyManhole,tmp])



nonDup_coveredNodesbyManhole=copy.deepcopy(pd.DataFrame(coveredNodesbyManhole.drop_duplicates()).reset_index(drop=True))

# prepare for optimization 
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# Fitness function
def evalFunc(individual):    

    coveredNodesbyManhole_4GA=pd.Series(dtype="float64")
    for i in range (len(individual)):        
        tmp=linkDownStreamDependentDB.iloc[:,individual[i]].dropna()
        coveredNodesbyManhole_4GA=pd.concat([coveredNodesbyManhole_4GA,tmp])
    coveredNodesbyManhole_4GA=pd.DataFrame(coveredNodesbyManhole_4GA).reset_index(drop=True)    
    
    
    ObservedLinks=coveredNodesbyManhole_4GA.drop_duplicates()
    totalLength=0.0
    for j in range (len(ObservedLinks)):
        length=LinkDB[LinkDB['Name']==ObservedLinks.iloc[j].values[0]]['Length'].values[0]
        #print("length = ", length)
        totalLength=totalLength+length
    print(totalLength)
    
    if totalLength>0:
        fitness=10000/totalLength
    else:
        fitness=10000
        
    #print("fitness ", fitness)
    
    del coveredNodesbyManhole_4GA    
    del ObservedLinks
    return fitness,


toolbox.register("evaluate", evalFunc)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)



def main(existing_sensor, n_sensor):
    # Total of possible sensor locations is 103 (0 to 102)
    #toolbox.register("attr_bool", random.randint, 0, 102)    
    
    available_manhole = [x for x in range(103) if x not in existing_sensor]
    toolbox.register("attr_bool", random.choice, available_manhole)        
    
    toolbox.register("individual", tools.initRepeat, creator.Individual,toolbox.attr_bool,n_sensor)
    # define the population to be a list of individuals
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    #random.seed(120)
    pop = toolbox.population(n=1000)    
    #print("pop: ", pop)
    pop_eval = copy.deepcopy(pop)
    for i in range(len(pop_eval)):
        pop_eval[i] = pop_eval[i] + existing_sensor
    
    # set up the initial values of crossover and mutation
    if n_sensor == 1:  # skip crossover if there is only one sensor
        CXPB, MUTPB = 0, 0.9
    else: 
        CXPB, MUTPB = 0.75, 0.06
        
    print("Start of evolution")
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop_eval))
    for ind, fit in zip(pop, fitnesses):
       # print(ind, fit)
        ind.fitness.values = fit
    
    print("  Evaluated %i individuals" % len(pop))
    # Extracting all the fitnesses of 
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0
    
    # Begin the evolution
    while max(fits) < 5000000 and g < 100:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
    
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):

            # cross two individuals with probability CXPB
            if random.random() < CXPB:
                toolbox.mate(child1, child2)

                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:

            # mutate an individual with probability MUTPB
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
    
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        
        invalid_ind_eval = copy.deepcopy(invalid_ind)
        for i in range(len(invalid_ind_eval)):
            invalid_ind_eval[i] = invalid_ind_eval[i] + existing_sensor
        
        fitnesses = map(toolbox.evaluate, invalid_ind_eval)
        for ind, fit in zip(invalid_ind, fitnesses):
            #print(ind, fit)
            ind.fitness.values = fit
        
        print("  Evaluated %i individuals" % len(invalid_ind))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]        
        
        #print("  Min Fitness %s" % min(fits))
        #print("  Max Fitness %s" % max(fits))
        best_ind = tools.selBest(pop, 1)[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    #best_ind_print = copy.deepcopy(best_ind)
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    #ii = 1
    #best_ind1 = tools.selBest(pop, ii+1)[ii]
    #while (best_ind1.fitness.values == best_ind.fitness.values) and ii < len(pop):
    #    best_ind_print.append(best_ind1)
    #    ii = ii + 1
    #    if ii < len(pop): 
    #        best_ind1 = tools.selBest(pop, ii+1)[ii]
    #return best_ind1
    return best_ind

existing_sensor = [11, 16, 25, 27, 33, 36, 44, 69, 79, 85] 

v_sensor = [1]*10 #for sequesntial method
for i in range(len(v_sensor)):
    out=main(existing_sensor, int(v_sensor[i]))    
    existing_sensor = existing_sensor + out
    print(existing_sensor)
    
saved_sensor = copy.deepcopy(existing_sensor)

n_sensor = 10 # for the simultaneous method
existing_sensor = [75, 56, 98, 22, 102, 46, 89, 35, 45, 55]
out=main(existing_sensor, int(n_sensor))


testing_64sensors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 25, 26, 29, 33, 34,36, 37, 39, 40, 46, 47, 48, 51, 52, 53, 56, 59, 61,63,64, 66,68, 70, 71, 73, 74, 75, 76, 78, 79, 83, 88, 89, 90, 92, 93, 94, 95, 97, 98, 100, 102]
print(evalFunc(testing_64sensors))
testing_47sensor = [1,3,	4,	5,	7,	8,	10,12, 13,	14	,16,	19,	21,	22,	24	,31,	32,	35,	37,	39,	41,	43,	47,	51,	52,
           54,	61,	63,	64,	66	,71,	73,	74	,75,	76	,78,	83	,88,	89	,90,	92,	93,	94,	95,	97,	102]
evalFunc(testing_47sensor)
print(evalFunc(testing_47sensor))


lengthcovered_existing_sensors = [11, 16, 25, 27, 33, 36, 44, 69, 79, 85]
print(evalFunc(lengthcovered_existing_sensors))


lengthcovered_10_sensors_simultaneous = [75, 45, 22, 55, 35, 89, 98, 56, 46, 83]
lengthcovered_10_sensors_simultaneous = [75, 56, 98, 22, 102, 46, 89, 35, 45, 55]
print(evalFunc(lengthcovered_10_sensors_simultaneous))

lengthcovered_10_sensors_senquential = [75, 41, 55, 54, 35, 89, 56, 98, 22, 83]
print(evalFunc(lengthcovered_10_sensors_senquential))

lengthcovered_20_optimal_sensors1 = [75, 89, 0, 55, 45, 93, 15, 22, 98, 61, 53, 102, 46, 66, 64, 100, 72, 35, 56, 32]
print(evalFunc(lengthcovered_20_optimal_sensors1))

lengthcovered_20_sensors2 = [75, 41, 55, 54, 35, 89, 56, 98, 22, 83, 102, 53, 32, 65, 72, 61, 71, 31, 79, 15]
print(evalFunc(lengthcovered_20_sensors2))

lengthcovered_20_sensors3 = [75, 45, 22, 55, 35, 89, 98, 56, 46, 83, 72, 71, 15, 61, 65, 53, 102, 31, 79, 32]
print(evalFunc(lengthcovered_20_sensors3))

lengthcovered_20_sensors4 = [75, 56, 98, 22, 102, 46, 89, 35, 45, 55, 93, 61, 32, 64, 83, 72, 31, 15, 66, 53]
print(evalFunc(lengthcovered_20_sensors4))

lengthcovered_20_sensors_existing = [11, 16, 25, 27, 33, 36, 44, 69, 79, 85,46, 56, 72, 55, 61, 102, 32, 75, 53, 89]
print(evalFunc(lengthcovered_20_sensors_existing))