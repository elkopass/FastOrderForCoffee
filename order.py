from audioop import add
from statistics import median
from tkinter import Menubutton
from turtle import pos, width
import telebot
from telebot import types
from datetime import datetime
import sqlite3
from sqlite3 import Error
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey, null
from datetime import datetime, timedelta
from sqlalchemy import insert, select
from sqlalchemy import  create_engine

engine = create_engine('sqlite:///sqlite3.db')

engine.connect()

metadata = MetaData()
users = Table('users', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('userId', String(200), nullable=False),
    Column('roleId', String(200),  nullable=False),
    )

orders = Table('orders', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('userId',  ForeignKey("users.id")),
    Column('status', String(200), nullable=False),
    Column('time', String(200),  nullable=False),
    )

positions = Table('positions', metadata, 
    Column('id', Integer(), primary_key=True),
    Column('name', String(200), nullable=False),
    Column('size', String(200),  nullable=False),
    )

pos_ord = Table('pos_ord', metadata,
    Column('pos_id', ForeignKey('positions.id')),
    Column('ord_id', ForeignKey('orders.id'))
)

def createDB():
   
    
    metadata.create_all(engine)
    
    #1
    ins = insert(users).values(
        userId = '2323232',
        roleId = '1'
    )
    conn = engine.connect()
    r = conn.execute(ins)
    print(r.inserted_primary_key)

    #2
    ins = insert(orders).values(
        userId = '1',
        status = 'new', 
        time = '12:30'
    )
    conn = engine.connect()
    r = conn.execute(ins)
    print(r.inserted_primary_key)

    #3
    ins = insert(positions).values(
        name = 'capuccino',
        size = 'normal'
    )
    conn = engine.connect()
    r = conn.execute(ins)
    print(r.inserted_primary_key)

    #4
    ins = insert(positions).values(
        name = 'americano',
        size = 'normal'
    )
    conn = engine.connect()
    r = conn.execute(ins)
    print(r.inserted_primary_key)
    
    #5
    ins = insert(pos_ord).values(
        pos_id = '1',
        ord_id = '1'
    )
    conn = engine.connect()
    r = conn.execute(ins)
    print(r.inserted_primary_key)

##createDB()


bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')



currentOrder = dict()
addings = dict()

# старт бота
@bot.message_handler(commands=['start'])
def start(message):
    print(type(message.chat.id))
    currentOrder[str(message.chat.id)] = []
    addings[str(message.chat.id)] = []
    addings[str(message.chat.id)] = []
    s = select([users]).where(
    users.c.userId == message.chat.id
    )
    conn = engine.connect()
    r = conn.execute(s)
    if(r.fetchall()==[]):
        ins = insert(users).values(
            userId = message.chat.id,
            roleId = 'user'
        )
        conn = engine.connect()
        r = conn.execute(ins)
        print(r.inserted_primary_key)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    item = types.KeyboardButton("Посмотреть заказ")
    item1 = types.KeyboardButton("Оформить заказ")
    markup.add(item)
    markup.add(item1)
    bot.send_message(message.chat.id, "Выберите позиции из меню", parse_mode='html', reply_markup= markup)
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    query = 'select * from menu where type=0'
    menu = cursor.execute(query).fetchall()

    keyboard = types.InlineKeyboardMarkup()

    for i in menu:
        
        key = types.InlineKeyboardButton(text=f"{i[1]} {i[2]}", callback_data= f"add {i[1]} {i[2]} {message.chat.id}")
        keyboard.add(key)

    bot.send_message(message.chat.id, 'Меню: ', reply_markup=keyboard)




timeVector = [0 for i in range(1440)]
def start_2(message):
    current_datetime = datetime.now()
    i  =  current_datetime.hour*60 + current_datetime.minute +  int(message.text) - 1
    while(timeVector[i] ==1 or timeVector[i+1] == 1):
        i += 1
        if(i > 1440):
            help_string = 'Слишком много заказов, попробуйте очно заказать кофе'
            bot.send_message(message.chat.id, help_string, parse_mode='html')

    timeVector[i] = 1
    timeVector[i+1] = 1
    timeOfWait = (i + 1) - (current_datetime.hour*60 + current_datetime.minute)
    help_string = f'Ваш заказ будет готов через: {timeOfWait} минут'
    bot.send_message(message.chat.id, help_string, parse_mode='html')
    
    print(currentOrder[str(message.chat.id)])
    
    #добавляем в БД заказ
    finT = current_datetime + timedelta(minutes=timeOfWait)
    tmp = finT.minute
    if(tmp > 0 and tmp < 10):
        finT = str(finT.hour) + str(':') + '0' + str(finT.minute)
    else:
        finT = str(finT.hour) + str(':') + str(finT.minute)
    print(type(finT))
    print(finT)
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()
    query = f"select id from users where userId = {message.chat.id}"
    print(query)
    idBD = cursor.execute(query).fetchone()[0]
    print(idBD)
    query = f"insert into orders (userId, status, time) values ({idBD},0,'{finT}')"
    print(query)
    cursor.execute(query)
    
    curOrderId = cursor.lastrowid
    for i in (currentOrder[str(message.chat.id)]):
        cursor.execute("insert into positions (size) values (1)")
        positionsId = cursor.lastrowid
        query = f"insert into pos_ord (pos_id, ord_id) values ({positionsId},{curOrderId})"
        cursor.execute(query)
        menuId = cursor.execute(f"select id from menu where name = '{i[0]}'").fetchone()[0] 
        print(i[0], i[1], i[2])
        print(type(i[2]))
        print(type(list(i[2])))
        for j in i[2]:
            print(j)
            if i[2] == []:
                query = f"insert into drink_add (drink_id, pos_id) values ({menuId},{positionsId})"
                cursor.execute(query)
            else:    
                addId = cursor.execute(f"select id from menu where name = '{j[0]}'").fetchone()[0] 
                query = f"insert into drink_add (drink_id, add_id, pos_id) values ({menuId}, {addId}, {positionsId})"
                cursor.execute(query)

    #сохранение изменений в бд
    conn.commit()
    
    
   

# команда-помощник
@bot.message_handler(commands=['help'])
def help(message):
    help_string = 'Это бот для баристы, который позволит Вам работать с заказами.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/orders - получить список активных заказов\n' \
                  '/?  (? - идентификатор заказа) - получить заказ по его идентификатору'

    bot.send_message(message.chat.id, help_string, parse_mode='html')



@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':

  
        if message.text == 'Посмотреть заказ':
            print(currentOrder[str(message.chat.id)])
            
            # tmp = ""
            # for i in currentOrder[str(message.chat.id)]:
                
            #     tmp += f"{i[0]} за  {i[1]} рублей "
            #     if(i[2] != []):
            #         tmp += "с добавками : \n"
            #     else: 
            #         tmp += '\n'
            #     for j in i[2]:
            #         tmp += f"{j[0]} за {j[1]} рублей \n"
            keyboard = types.InlineKeyboardMarkup() 
            tmp = 0
            for i in currentOrder[str(message.chat.id)]:  
                key = types.InlineKeyboardButton(text = f"{i[0]} {i[1]}", callback_data= f"look {tmp} {message.chat.id}") 
                keyboard.add(key)

                tmp += 1
            bot.send_message(message.chat.id, "Ваш заказ:", reply_markup=keyboard)
            
           # bot.delete_message(message.chat.id, message.id)

        elif message.text == 'Оформить заказ':
            curPrice = 0
            print(currentOrder[str(message.chat.id)])
            for i in currentOrder[str(message.chat.id)]:
                curPrice += int(i[1])
                for j in i[2]:
                    curPrice += int(j[1])

            keyboard = types.InlineKeyboardMarkup()
            key = types.InlineKeyboardButton(text = "Да", callback_data= f"send {message.chat.id}")
            key1 = types.InlineKeyboardButton(text = "Назад", callback_data= f"back  {message.chat.id}")
            keyboard.add(key)
            keyboard.add(key1)
            bot.send_message(message.chat.id, f"Ваш заказ будет стоить {curPrice} рублей. \n Оформить заказ?", reply_markup=keyboard)
            print(curPrice)
           

       

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    state = call.data.split()[0]
    if state == "back":
        
        addings[str(call.message.chat.id)] = []
        bot.delete_message(call.message.chat.id, call.message.id)
        conn = sqlite3.connect('sqlite3.db')
        cursor = conn.cursor()

        query = 'select * from menu where type=0'
        menu = cursor.execute(query).fetchall()

        keyboard = types.InlineKeyboardMarkup()

        for i in menu:
            key = types.InlineKeyboardButton(text=f"{i[1]} {i[2]}", callback_data= f"add {i[1]} {i[2]} {call.message.chat.id}")
            keyboard.add(key)

        bot.send_message(call.message.chat.id, 'Меню: ', reply_markup=keyboard)

    elif state == "send":
        
        msg = bot.send_message(call.message.chat.id, 'Через сколько минут вам хотелось бы забрать кофе ?')
        bot.register_next_step_handler(msg, start_2)

    elif state == "look":
        id = call.data.split()[1]
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton(text=f"Удалить позицию", callback_data= f"del {id} {call.message.chat.id}")
        keyboard.add(key)
        tmp = 0
        for i in currentOrder[str(call.message.chat.id)][int(id)][2]:
            key = types.InlineKeyboardButton(text=f" Удалить {i[0]} стоимостью {i[1]} рублей", callback_data= f"delAdd {id} {tmp} {call.message.chat.id}")
            keyboard.add(key)
            tmp += 1

        bot.send_message(call.message.chat.id, f"{currentOrder[str(call.message.chat.id)][int(id)][0]} {currentOrder[str(call.message.chat.id)][int(id)][1]}", reply_markup=keyboard)

    elif state == "delAdd":
        id = call.data.split()[1]
        idAdd = call.data.split()[2]
        currentOrder[str(call.message.chat.id)][int(id)][2].pop(int(idAdd))

        keyboard = types.InlineKeyboardMarkup() 
        tmp = 0
        for i in currentOrder[str(call.message.chat.id)]:  
            key = types.InlineKeyboardButton(text = f"{i[0]} {i[1]}", callback_data= f"look {tmp} {call.message.chat.id}") 
            keyboard.add(key)

            tmp += 1
        bot.send_message(call.message.chat.id, "Ваш заказ:", reply_markup=keyboard)

    elif state == "del":

        id = call.data.split()[1]
        currentOrder[str(call.message.chat.id)].pop(int(id))

        keyboard = types.InlineKeyboardMarkup() 
        tmp = 0
        for i in currentOrder[str(call.message.chat.id)]:  
            key = types.InlineKeyboardButton(text = f"{i[0]} {i[1]}", callback_data= f"look {tmp} {call.message.chat.id}") 
            keyboard.add(key)

            tmp += 1
        bot.send_message(call.message.chat.id, "Ваш заказ:", reply_markup=keyboard)
    else:
        
        name = call.data.split()[1]
        price = call.data.split()[2]
        id = call.data.split()[3]
        if state == "add":
            
            bot.delete_message(call.message.chat.id, call.message.id)
            keyboard = types.InlineKeyboardMarkup()
            key = types.InlineKeyboardButton(text = "Добавить в заказ", callback_data= f"finalAdd {name} {price} {call.message.chat.id}")
            key1 = types.InlineKeyboardButton(text = "Добавки",callback_data= f"addings {name} {price} {call.message.chat.id}" )
            key2 = types.InlineKeyboardButton(text = "Вернуться в меню", callback_data= f"back")
            keyboard.add(key)
            keyboard.add(key1)
            keyboard.add(key2)
            bot.send_message(call.message.chat.id, f"{name} {price}", reply_markup=keyboard)

        elif state == "addings":
            bot.delete_message(call.message.chat.id, call.message.id)
            conn = sqlite3.connect('sqlite3.db')
            cursor = conn.cursor()

            query = 'select * from menu where type=1'
            menu = cursor.execute(query).fetchall()
            print(menu)
            keyboard = types.InlineKeyboardMarkup()

            for i in menu:
                key = types.InlineKeyboardButton(text=f"Добавить {i[1]} за {i[2]} рублей", callback_data= f"newAdding  {i[1]} {i[2]} {call.message.chat.id}")
                keyboard.add(key)

            key = types.InlineKeyboardButton(text="Назад", callback_data=f"add {name} {price} {call.message.chat.id}")
            keyboard.add(key)

            bot.send_message(call.message.chat.id, 'Добавки: ', reply_markup=keyboard)
        elif state == "finalAdd":
            
            currentOrder[str(id)].append([f"{name}", f"{price}", addings[str(id)]])
            bot.send_message(call.message.chat.id, f" заказ добавлен: \n {name} {price}")
            print(currentOrder[str(id)])
            addings[str(id)] = []
        elif state == "newAdding":
            addings[str(id)].append([name, price])
            print(addings[str(id)])

    bot.answer_callback_query(call.id)

bot.polling(non_stop= True)