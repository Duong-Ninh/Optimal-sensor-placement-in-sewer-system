# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 09:28:45 2022

@author: Thi Hai Duong Ninh-a1643537
"""
# ## Optimal sensor locations for maximizing network coverage using GA

# #### System 1


import random
from deap import base
from deap import creator
from deap import tools
import numpy as np
import pandas as pd
import copy


# In[2]:


# Import data from Topological solution, which is saved under the pread sheet "DownstreamDependent"
fileName='U:\phd_program_ninh\Data and code\paper1\System1_network.xlsx'
DownStreamDependentDB=pd.read_excel(fileName,sheet_name='DownstreamDependent')


# In[3]:


#Find all covered nodes
coveredNodesbyManhole=pd.Series(dtype="float64")
for i in range (DownStreamDependentDB.shape[1]):
    tmp=DownStreamDependentDB.iloc[:,i].dropna()
    coveredNodesbyManhole=pd.concat([coveredNodesbyManhole,tmp]) #creat a vector of covered Nodes by Manholes


# In[4]:

coveredNodesbyManhole=pd.DataFrame(coveredNodesbyManhole).reset_index()
#nonDup_coveredNodesbyManhole=copy.deepcopy(pd.DataFrame(coveredNodesbyManhole.drop_duplicates()).reset_index())
nonDup_coveredNodesbyManhole=copy.deepcopy(pd.DataFrame(coveredNodesbyManhole.drop_duplicates(subset=[0])).reset_index())
                            
# nonDup_coveredNodesbyManhole means removing all duplcated nodes to crate a set of nodes of entire network 

# In[7]:


# prepare for optimization 
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,toolbox.attr_bool, 103)
# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Fitness function
def evalFunc(individual):
    
    coveredNodesbyManhole_4GA=pd.Series(dtype="float64")
    for i in range (len(individual)):  #range (0, 103)
        if (individual[i]==1):
            tmp=DownStreamDependentDB.iloc[:,i].dropna()
            coveredNodesbyManhole_4GA=pd.concat([coveredNodesbyManhole_4GA,tmp])
    coveredNodesbyManhole_4GA=pd.DataFrame(coveredNodesbyManhole_4GA).reset_index()   

#count duplicates of coveredNodesbyManhole_4GA and nonDup_coveredNodesbyManhole
    countObserved_4GA=[] 
    for i in range (len(nonDup_coveredNodesbyManhole)):    # range(0, 429)
        tmp=np.sum(coveredNodesbyManhole_4GA[0]==nonDup_coveredNodesbyManhole[0][i])# if it is equal--> true (1), else-->false (0)
        countObserved_4GA.append(tmp)
    pen=0
    fit=0
    fitness=0;
    for i in range(len(countObserved_4GA)):   #length:429
        fit=fit+countObserved_4GA[i]
        if (countObserved_4GA[i]==0): 
           pen=pen+1000
   
            
    fitness=pen+fit               
    
    del coveredNodesbyManhole_4GA    
    del countObserved_4GA
    return fitness,
toolbox.register("evaluate", evalFunc)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)


# In[8]:


def main():
    random.seed(100)
    pop = toolbox.population(n=100)
    CXPB, MUTPB = 0.75, 0.06
    print("Start of evolution")
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    print("  Evaluated %i individuals" % len(pop))
    # Extracting all the fitnesses of 
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0
    
    # Begin the evolution
    while max(fits) < 5000000 and g < 200:
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
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        print("  Evaluated %i individuals" % len(invalid_ind))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]        
        
        print("  Min Fitness %s" % min(fits))
        print("  Max Fitness %s" % max(fits))
    
    print("-- End of (successful) evolution --")
    
    best_ind = tools.selBest(pop, 1)[0]
    print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
    return best_ind
    


# In[9]:


## Run GA
## Don't need to run anymore after saving result to System1_network.xlsx

out=main()

## Get result from GA

ManholeID=pd.read_excel(fileName,sheet_name='ManholeLocation')
out=pd.DataFrame(out)
sens=ManholeID['ID']*out[0]

active=[]
for i in range (len(ManholeID)):
    if (out[0][i]==1):
        tmp=ManholeID.index[i]
        active.append(tmp)


# In[10]:


out.to_csv('Ga_out_minimise_sensors_System1_70%Manhole.csv')



