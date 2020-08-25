# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 15:17:26 2020

@author: qtckp
"""

import numpy as np


def currect_diff(borders, sample):
    
    res = borders - sample
    res[0,:] = np.maximum(0, res[0,:])
    return res


def is_valid_diff(difference):
    return  np.sum(difference[1,:] < 0) == 0  # all((v>=0 for v in difference[2,:]))








def get_day(foods, recipes, borders, recipes_samples = 10):
    
    # recipes part
    
    recipes_inds = np.random.choice(recipes.shape[0], recipes_samples)
    
    recipes_used = recipes[recipes_inds,:]
        
    counts = np.zeros(recipes_samples)
    
    bord = borders[0:2,:].copy()

    while True:
        
        no_progress = 0
        
        for i in range(recipes_samples):
            
            new_bord = currect_diff(bord, recipes_used[i,:])

            if is_valid_diff(new_bord):
                bord = new_bord
                counts[i] += 1
            else:
                no_progress += 1
        
        if no_progress == recipes_samples:
            break
    
    # foods part
    
    food_size = foods.shape[0]
    
    food_inds = np.arange(food_size)
    np.random.shuffle(food_inds)


    counts2 = np.zeros(food_size)
    
    for i in range(food_size):
        
        while True:
            new_bord = currect_diff(bord, foods[food_inds[i],:])
            
            if is_valid_diff(new_bord):
                bord = new_bord
                counts2[i] += 1
            else:
                break
    
    
    
    # currect weights
            
    recipes_weights = np.zeros(recipes.shape[0])
    recipes_weights[recipes_inds] = counts
    print(recipes_weights)
    
    food_weights = np.zeros(food_size)
    food_weights[food_inds] = counts2
    print(food_weights)
    
    # results
    
    r = np.sum(recipes * recipes_weights.reshape(recipes.shape[0], 1), axis = 0)
    f = np.sum(foods * food_weights.reshape(food_size, 1), axis = 0)
    
    print(r + f < borders[0,:])
    
    assert(np.sum(r + f < borders[0,:]) == 0)
    
    # это условие всегда выполнено из смысла самого алгоритма
    assert(np.sum(r + f > borders[1,:]) == 0)










# import pandas as pd

# foods = pd.read_csv('currect_foods.csv')

# food_names = foods.name
# foods = foods.iloc[:,:-1].to_numpy()


# recipes = pd.read_csv('currect_recipes.csv')

# recipes_names = recipes.name
# recipes = recipes.iloc[:,:-1].to_numpy()


# borders = pd.read_csv('currect_borders.csv').to_numpy()


#get_day(foods, recipes, borders[0:2,:], 10)




np.random.seed(1)
pred_count = 80

food_wrap = np.random.uniform(low = 0.5, high = 3, size = (100, pred_count))
recipes_wrap = np.random.uniform(low = 2, high = 4, size = (150, pred_count))


a = np.random.normal(loc = 50, scale = 5, size = pred_count)
b = np.random.normal(loc = 60, scale = 3, size = pred_count)

borders_wrap  = np.vstack((
        a,
        a + np.random.uniform(low = 5, high = 10, size = pred_count),
        b,
        b + np.random.uniform(low = 1.5, high = 3, size = pred_count)
    ))

np.sum(borders_wrap [3,:] > borders_wrap [2,:])
np.sum(borders_wrap [1,:] > borders_wrap [0,:])



get_day(food_wrap , recipes_wrap , borders_wrap[0:2,:], 7)













