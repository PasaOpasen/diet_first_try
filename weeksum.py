# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 13:18:21 2020

@author: qtckp
"""


def get7sum(limit = 3):
    """
    возвращает комбинации чисел от 1 до 7, которые в сумме дают 7
    
    это рассматривается как сколько дней в неделю повторяется один рецепт из нескольких
    
    например, ответ 2 2 3 -- это 2 дня в неделю первый рецепт, 2 -- второй и 3 -- третий
    
    возвращается словарь, ключи которого значат, сколько разных рецептов использовалось,
    а значения -- это списки разных вариантов
    
    аргумент limit значит сколько максимально раз можно использовать один и тот же рецепт (есть 7 раз в неделю одинаково вряд ли кому-то понравится)
    """
    
    if limit > 7:
        limit = 7

    comps = list(range(1,7)) # days of week
    
    results = []#[([1],1)]
    
    for c in comps:
        for _ in range(limit):
            tmp = [([c], c)]
            for r, s in results:
                if s + c <= 7:
                    tmp.append((r + [c], s + c))
            results += tmp
    
    tmp = [sorted(r) for r, s in results if s == 7]
    
    answer = []
    for t in tmp:
        if t not in answer:
            answer.append(t)
        
    #return answer
            
    dic = {}
    for i in range(1,8):
        dic[i] = []
    for a in answer:
        dic[len(a)].append(a)
    
    dic[1] = [[7]]
    
    return dic





if __name__ == '__main__':
    
    get7sum(5)

