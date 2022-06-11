from audioop import add
from statistics import median
from tkinter import Menubutton
from turtle import pos, width
import telebot
from telebot import types
from datetime import datetime
import sqlite3
from sqlite3 import Error
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy import insert, select
from sqlalchemy import  create_engine

ordersORM = dict()

engine = create_engine('sqlite:///sqlite3.db')

engine.connect()

print(engine)
param = {'Size': 0,'Addings': []}

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
class Order:
    def __init__(self, id, code, arrayOfPositions , status, time): 
        self.id = id 
        self.code = code
        self.arrayOfPositions = arrayOfPositions
        self.status = status
        self.time = time
 
    def display(self): 
        print("ID: %d nName: %s" % (self.id, self.code)) 

    def setPosition(self, position):
        self.arrayOfPositions.append(position)


# order = Order(2, 5,[] ,"new" , "00:00")
# order.display()
def sendOrder(Order):
    ## send order
    print("Order is send") 

# старт бота
@bot.message_handler(commands=['start'])
def start(message):
    help_string = 'бот запущен'

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
    item1 = types.KeyboardButton("Посмотреть меню")
    item2 = types.KeyboardButton("Сделать заказ")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, help_string, parse_mode='html', reply_markup= markup)

# алгоритм для подсчета времени ожидания
@bot.message_handler(commands=['order'])
def start(message):
    msg = bot.send_message(message.chat.id, 'Через сколько минут вы придете за кофе')
    bot.register_next_step_handler(msg, start_2)


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
 
    print(timeVector[899:950])


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
        if message.text == 'Кофе':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Капучино")
            item2 = types.KeyboardButton("Экспрессо")
            back = types.KeyboardButton("Назад")

            markup.add(item1, item2, back)

            bot.send_message(message.chat.id, 'Кофе', reply_markup= markup)

        elif message.text == 'Капучино':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Банановый коктейль")
            back = types.KeyboardButton("Назад")

            markup.add(item1, back)

            bot.send_message(message.chat.id, 'Капучино', reply_markup= markup)
        
        elif message.text == 'Экспрессо':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Банановый коктейль")
            back = types.KeyboardButton("Назад")

            markup.add(item1, back)

            bot.send_message(message.chat.id, 'Экспрессо', reply_markup= markup)
        
    


        elif message.text == 'Холодные напитки':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Банановый коктейль")
            back = types.KeyboardButton("Назад")

            markup.add(item1, back)

            bot.send_message(message.chat.id, 'Холодные напитки', reply_markup= markup)
        elif message.text == 'Закуски':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Сэндвич")
            item2 = types.KeyboardButton("Круасан")
            back = types.KeyboardButton("Назад")

            markup.add(item1, item2, back)

            bot.send_message(message.chat.id, 'Закуски', reply_markup= markup)

        elif message.text == 'Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
            item1 = types.KeyboardButton("Кофе")
            item2 = types.KeyboardButton("Холодные напитки")
            item3 = types.KeyboardButton("Закуски")

            markup.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Назад', reply_markup= markup)
        
        
        elif message.text == "Посмотреть меню":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Капучино 75 рублей', callback_data= "gg")
            key2 = types.InlineKeyboardButton(text='Американо 110 рублей', callback_data= "gg")
            key3 = types.InlineKeyboardButton(text='Милкшейк 150 рублей ', callback_data= "gg")
            key4 = types.InlineKeyboardButton(text='Сэндвич 130 рублей', callback_data= "gg")
            key5 = types.InlineKeyboardButton(text='Шоколадный Маффин 30 рублей', callback_data= "gg")

            keyboard.add(key1)
            keyboard.add(key2)
            keyboard.add(key3)
            keyboard.add(key4)
            keyboard.add(key5)
            bot.send_message(message.chat.id, 'Посмотреть меню', reply_markup=keyboard)
            bot.delete_message(message.chat.id, message.id)
        
        elif message.text == 'Сделать заказ':
            

            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Добавить Капучино', callback_data= f"add {message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Убрать Капучино', callback_data= f"rem {message.chat.id}")
            item3 = types.InlineKeyboardButton("Посмотреть заказ", callback_data= "gg")
            keyboard.add(key1, key2)
            keyboard.add(item3)
            ordersORM[message.chat.id] = []
            bot.send_message(message.chat.id, 'Выберите позицию', reply_markup=keyboard)
           
          

        elif message.text == 'Посмотреть заказ ':
            print(ordersORM[message.chat.id])
            tmp = ""
            for i in ordersORM[message.chat.id]:
                tmp += f"{i}\n"
            bot.send_message(message.chat.id, tmp)
            
            bot.delete_message(message.chat.id, message.id)

       

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    state = call.data.split()[0]
    
    if state == "gg":
        bot.answer_callback_query(call.id)
        return
    else:
        bot.delete_message(call.message.chat.id, call.message.id)
        id = int(call.data.split()[1])
        if state == "add":  
            ordersORM[id].append('Kапучино')
            param['Addings'] = []
            param['Size'] = ""
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "rem":
            if (('Kапучино' in ordersORM[id]) == False):
                
                    bot.send_message(id, 'У вас и так нет капучино в заказе')
            else:
                ordersORM[id].remove('Kапучино')
        elif state =="size":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Средний', callback_data= f"med {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Большой', callback_data= f"sml {call.message.chat.id}")
            
            keyboard.add(key1, key2)
            
            bot.send_message(call.message.chat.id, 'Выберите размер:', reply_markup=keyboard)
        elif state == "adding":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Шоколадная крошка', callback_data= f"addings {call.message.chat.id}")
            keyboard.add(key1)
            bot.send_message(call.message.chat.id, 'Выберите добавку:', reply_markup=keyboard)
        elif state == "sml":
            param['Size'] = "Cредний"
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "med":
            param['Size'] = "Большой"
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
           
            
        elif state == "addings":
            param['Addings'].append("Sugar")
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "sendP":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Добавить Капучино', callback_data= f"add {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Убрать Капучино', callback_data= f"rem {call.message.chat.id}")
            item3 = types.InlineKeyboardButton("Посмотреть заказ", callback_data= f"check {call.message.chat.id}")
            item4 = types.InlineKeyboardButton("Отправить заказ", callback_data= f"sendO {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(item3, item4)
            
            bot.send_message(call.message.chat.id, 'Выберите позицию:', reply_markup=keyboard)
        elif state == "sendO":  
            msg = bot.send_message(call.message.chat.id, 'Через сколько минут вам хотелось бы забрать кофе')
            bot.register_next_step_handler(msg, start_2)
            
        elif state == "check":
            str1 = ""
            for i in param['Addings']:
                if (i == "Sugar"):
                    str1 +=  "Шоколадная крошка "
            
            bot.send_message(call.message.chat.id, f'Позиции: {ordersORM[id][0]}\n Размер: {param["Size"]} \n Добавки: {str1} ')
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='ДА', callback_data= f"sendO {call.message.chat.id}")
            keyboard.add(key1)
            bot.send_message(call.message.chat.id, 'Отправить заказ ?', reply_markup=keyboard)


    print(ordersORM[id])
    print(id)
    print(param)
    bot.answer_callback_query(call.id)

bot.polling(non_stop= True)