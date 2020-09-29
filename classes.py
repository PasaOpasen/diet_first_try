# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:36:47 2020

@author: qtckp
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json

from split_day import splitDay




def get_dict(names, values):
    return {n: v for n, v in zip(names, values)}




class Day:
    """
    суть построения дня такая:
        главное в дне -- это чтоб он попадал в границы, из этого метода дни и генерируются
        
        всякая информация по поводу разбиения на приёмы пищи или дополнительных напитков -- это уже вторичные вещи,
        которые должны добавляться к дню отдельно, ибо они нужны только для валидных дней и генерируются не обязательно мгновенно
    """
    def __init__(self, recipes_weights, food_weights, combination = 0, less_than_down = None):
        self.recipes_weights = recipes_weights
        self.food_weights = food_weights
        self.combination = combination
        self.less_than_down = less_than_down
        self.splitted = {}
        self.drinks = None
        
        
    def show_info(self):
        
        ri = {i: r for i, r in enumerate(self.recipes_weights) if r != 0}
        fi = {i: f for i, f in enumerate(self.food_weights) if f != 0}
        
        print('recipes index: count')
        print(ri)
        print()
        print('food index: count')
        print(fi)
        print()
        print(f'result: {self.combination} with {self.less_than_down} lesses under lower border')
    
    
    def set_splitter(self, indexes, sums = [[15,10], 40, 35], max_tryes = 20):
        """
        создает разбиение дня в соответствии с процентами sums
        
        пробует сделать это максимум max_tryes раз, в случае неудачи никак не меняет self.splitted
        
        нужно делать разные попытки, потому что в зависимости от начального разбиения по классам
        алгоритм может не сойтись, поэтому для каждой новой попытки индексы (хотя бы некоторая их часть)
        должны принимать случайные значения
        """
        
        mt = indexes['meal_time']
        f = mt['foods']
        r = mt['recipes']
        
        for _ in range(max_tryes):
            recipes_time = np.random.choice([1,3,5], r.size, replace = True)
            recipes_time[r > 0] = r[r > 0]
            
            foods_time = np.random.choice([1,3,5], f.size, replace = True)
            foods_time[f > 0] = f[f > 0]
            
            ans = splitDay(indexes['recipes_energy'], indexes['foods_enegry'], 
                           self.recipes_weights, self.food_weights, 
                           indexes['recipes_names'], indexes['foods_names'], 
                           recipes_time, foods_time, sums = sums, random_labels = None)
            if ans != None:
                self.splitted = ans
                return
        
    
    def to_dictionary(self, indexes, sums = [[15,10], 40, 35]):
        
        answer = {
            'recipes':[],
            'foods':[],
            'combination': get_dict(indexes['goal_columns'],self.combination), #self.combination.tolist(),
            'lower_error': int(self.less_than_down),
            'water':{}
                  }
        
        for i, r in enumerate(self.recipes_weights):
            if r != 0:
                answer['recipes'].append({
                    'index': indexes['recipes_names'][i],
                    'count': int(r)
                    })
        answer['water']['recipes'] = np.sum(indexes['water']['recipes'] * self.recipes_weights)
                
        
        for i, f in enumerate(self.food_weights):
            if f != 0:
                answer['foods'].append({
                    'index': indexes['foods_names'][i],
                    'count': float(f/2) #int(f)
                    })
        answer['water']['foods']= np.sum(indexes['water']['foods'] * self.food_weights)
        
        
        # если сплит не считался или не был найден, поискать
        if not bool(self.splitted):
            self.set_splitter(indexes, sums)
        
        answer['split'] = self.splitted
        
        # если напитки были созданы, добавить
        if self.drinks != None:
            answer['drinks'] = self.drinks
        
        
        return answer
    
    def to_json(self, file_name, indexes, sums = [[15,10], 40, 35]):
        
        dictionary = self.to_dictionary(indexes, sums)
        
        with open(file_name, "w") as write_file:
            json.dump(dictionary, write_file, indent = 4)
            
    def plot(self, file_name, indexes, borders):
        """
        делает упрощённый рисунок
        """
        
        df = pd.DataFrame({
            'nutrients': indexes['goal_columns'],
            'current result': self.combination/borders[1,:]*100,
            'lower border': borders[0,:]/borders[1,:]*100,
            'upper border': borders[1,:]/borders[1,:]*100
            })
        
        fig, ax = plt.subplots()
        

        
        
        df.plot(kind= 'line', x='nutrients', y='upper border', ax = ax, color = 'red', marker = 'o')
        
        df.plot(kind= 'line', x='nutrients', y='lower border', ax = ax, color = 'black', marker = 'o')
        
        df.plot(kind='bar',x='nutrients', y='current result', ax = ax)
        
        ax.set_xticklabels(df['nutrients'], rotation=90)
        
        plt.savefig(file_name, dpi = 350, bbox_inches = "tight")
        
        plt.close()
        
    
    def plot2(self, file_name, indexes, borders, foods, recipes):
        """
        работает как plot, только делает ещё разбиение по recipes/foods
        и некоторые дополнительные объекты
        """
        
        df = pd.DataFrame({
            'nutrients': indexes['goal_columns'],
            'current result': self.combination/borders[1,:]*100,
            'by recipes': self.recipes_weights.dot(recipes)/borders[1,:]*100,
            'by foods': self.food_weights.dot(foods)/borders[1,:]*100,
            'lower border': borders[0,:]/borders[1,:]*100,
            'upper border': borders[1,:]/borders[1,:]*100,
            'ideal': borders[4,:]/borders[1,:]*100
            })
        
        
        #print(np.allclose(df['current result'].values, (df['by recipes'] + df['by foods']).values))
        
        df['by foods'] = df['by recipes'] + df['by foods']
        
        fig, ax = plt.subplots()
        

        df.plot(kind= 'line', x='nutrients', y='upper border', ax = ax, color = 'red', marker = 'o')
        
        df.plot(kind= 'line', x='nutrients', y='lower border', ax = ax, color = 'black', marker = 'o')
        
        df.plot(kind= 'line', x='nutrients', y='ideal', ax = ax, color = 'violet', linestyle='dashed', marker = 'X')
        
        df.plot(kind='bar',x='nutrients', y='by foods', ax = ax)
        df.plot(kind='bar',x='nutrients', y='by recipes', ax = ax, color="C2")
        
        ax.set_xticklabels(df['nutrients'], rotation=90)
        
        plt.savefig(file_name, dpi = 350, bbox_inches = "tight")
        
        plt.close()

                
        

class Weeks:
    """
    неделя -- это набор дней в такой пропорции, чтобы усреднение по дням попадало в недельные границы
    """
    def __init__(self, days, configs, score, lower, upper):
        self.days = days
        self.configurations = configs
        self.score = score
        self.lower = lower
        self.upper = upper
        
    def show_info(self):
        print(f'I have {len(self.days)} days')
        print(f'My combination: {self.configurations[0]}')
        print(f'Vector: {self.configurations[1]}')
        print(f'score = {self.score}')
        print(f'lower error is {self.lower}, upper error is {self.upper}')
        
    def to_dictionary(self, indexes):
        answer = {
            
            'vector_of_combination': get_dict(indexes['goal_columns'], self.configurations[1]), #self.configurations[1].tolist(),
            'score': self.score,
            'lower_error': int(self.lower),
            'upper_error': int(self.upper),
            'days_in_week': [],
                  }
        
        for day , count in zip(self.days, self.configurations[0]):
            answer['days_in_week'].append({
                'day': day.to_dictionary(indexes),
                'repeats_in_week': int(count)
                })
        
        return answer
    
    def to_json(self, file_name, indexes):
        dictionary = self.to_dictionary(indexes)
        
        with open(file_name, "w") as write_file:
            json.dump(dictionary, write_file, indent = 4)
        