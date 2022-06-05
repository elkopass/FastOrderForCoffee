
from array import array
import telebot
from telebot import types
from datetime import datetime

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

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



bot.polling(none_stop=True)