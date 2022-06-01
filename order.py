
from array import array
from statistics import median
import telebot
from telebot import types
from datetime import datetime

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
    item1 = types.KeyboardButton("Кофе")
    item2 = types.KeyboardButton("Холодные напитки")
    item3 = types.KeyboardButton("Закуски")

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, 'Выбери'.format(message.from_user), reply_markup= markup)
    
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

bot.polling(non_stop= True)