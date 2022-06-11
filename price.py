from typing import final


id  =  123 # id пользователя
pos = 3 #количество позиций в заказе пользователя с id  = 123
ordersORM = dict() 
ordersORM[id].add([1,2,3]) #заказ пользователя, где цифра - отдельная позиция 
param = dict()
param[id].add([])
for i in range(pos):
    param[id].append({'Size': 0,'Addings': []}) #Добавки пользователю

for i in ordersORM[id]:
    finalprice = 0
    if i =='Капучино':
        finalprice += 75
    if param[id][i]['Size'] == 1:
        finalprice += 50
    if  param[id][i]['Addings'] == "Suagr":
        finalprice += 15