# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 12:14:13 2020

@author: qtckp
"""


import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import json
import warnings
from collections import namedtuple

# my modules
from weeksum import get7sum
from loading import get_data
from little_functions import currect_diff, is_between, is_valid_diff, will_be_valid_diff, MAPE
from classes import Day, Weeks


from method_draft import get_day_fullrandom9, get_drinks_ways



# это варианты суммы из условий

SUMS = {
        '3x': [25, 45, 30],
        '4x': [25,35,[15,25]],
        '5x': [[25,10], [35,10], 20],
        '6x': [[20,10],[35,10],[20,5]],
        'night': [[10,15],25,[30,15]]
        }




def get_optimal_days(patient = 'norms.txt', prefix ='',
                     how_many_days = 6, max_tryes_for_days = 100,
                     recipes_samples = 10, max_recipes_count = 3, max_food_count = 15, food_tryes = 10, return_first_with_error = 3, max_error_count = 4, 
                     sums = [[15,10], 40, 35],
                     needed_water = 3000, max_drinks_samples = 4, max_drinks_count = 3, drinks_samples_count = 10, max_iterations_for_drinks = 100,
                     save_to_json = True, plot = True,
                     return_as_json = False):
    """
    Возращает оптимальные дни при нужных условиях

    Parameters
    ----------
    patient : строка, optional
        название файла с нормами или его содержание как json. The default is 'norms.txt'.
    prefix : строка, optional
        префикс, который будет добавлен в названия файлов. The default is ''.
    how_many_days : int, optional
        как много дней нужно сгенерировать. The default is 6.
    max_tryes_for_days : int, optional
        максимальное число попыток для получения первого дня; если прошло столько попыток, а день не найден, выдаётся исключение. The default is 100.
    recipes_samples : int, optional
        сколько разных рецептов допустимо использовать в одном дне. The default is 10.
    max_recipes_count : int, optional
        сколько максимально раз может повторяться каждый рецепт в одном дне. The default is 3.
    max_food_count : int, optional
        сколько максимально раз может повторяться каждый food в одном дне. The default is 15.
    food_tryes : int, optional
        столько раз для каждого дня ищется оптимальный расклад по foods, потом выбирается лучший. Чем меньше, тем быстрее, но хуже. The default is 10.
    return_first_with_error : int, optional
        как только возникает комбинация с таким числом несоответствий, она возвращается как оптимальная и поиски прекращаются. The default is 3.
    max_error_count : int, optional
        какое число несоотвествий по цели считается допустимым. The default is 4.
    sums : TYPE, optional
        суммы процентов для разбиения по приёмам пищи. The default is [[15,10], 40, 35].
    needed_water : TYPE, optional
        сколько всего воды нужно пациенту (вообще эта информация должна бы быть в norms). The default is 3000.
    max_drinks_samples : int, optional
        сколько разных напитков допустимо использовать в одном дне. The default is 4.
    max_drinks_count : int, optional
        сколько раз можно использовать каждый напиток в одном дне. The default is 3.
    drinks_samples_count : int, optional
        сколько конфигураций по напиткам нужно вернуть (сколько разных вариантов). The default is 10.
    max_iterations_for_drinks : int, optional
        число попыток для поиска указанного числа конфигураций. The default is 100.
    save_to_json : bool, optional
        сохранять ли полученные дни в json (если True, каждый день в отдельности будет сохранён). The default is True.
    plot : bool, optional
        сохранять ли изображения. The default is True.
    return_as_json : bool, optional
        возвращать ли полученный словарь как строку json (иначе словарь python). The default is False.

    Raises
    ------
    Exception
        выдает сообщение, если не получилось найти хотя бы 1 день.

    Returns
    -------
    словарь как json или python (зависит от return_as_json), полученные дни как список экземпляров класса Day

    """
    
    
    # getting data
    foods, recipes, borders, drinks, indexes = get_data(patient)
    
    
    # getting valid days
    days = []
    counter = 0
    
    while len(days) < how_many_days:
        
        cand = get_day_fullrandom9(foods, recipes, borders, recipes_samples, max_recipes_count, max_food_count, food_tryes, return_first_with_error)
    
        if cand.less_than_down <= max_error_count:
            days.append(cand)
        else:
            counter += 1
            
        if len(days) == 0 and counter == max_tryes_for_days:
            raise Exception(f'Не получилось найти хотя бы 1 валидный день за {max_tryes_for_days} попыток. Попробуйте смягчить условия')
    
    
    # getting drinks
    
    for day in days:
        day.drinks = get_drinks_ways(needed_water, day, drinks, borders, indexes, max_drinks_samples, max_drinks_count, drinks_samples_count, max_iterations_for_drinks)
    
    
    # getting split and save to json
    if save_to_json:
        for i, day in enumerate(days):
            
            day.to_json(f'results/{prefix} day {i+1}.json', indexes, sums)

    
    if plot:
        for i, day in enumerate(days):
            day.plot2(f'results/{prefix} day {i+1}.png', indexes, borders, foods, recipes)
            
    
    #return [day.to_dictionary(indexes, sums) for day in days]
            
    result_as_dictionary = {f'{prefix}_day_{i+1}': day.to_dictionary(indexes, sums, rewrite = False) for i, day in enumerate(days)}
    return json.dumps(result_as_dictionary, indent = 4) if return_as_json else result_as_dictionary, days





if __name__ == '__main__':

    answer, days = get_optimal_days(prefix = 'default', save_to_json = False, return_as_json = True)
    
    answers = {}
    for time, val in SUMS.items():
        
        answers[time], days = get_optimal_days(sums = val, prefix = time)




