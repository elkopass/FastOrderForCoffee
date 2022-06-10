import telebot
from telebot import types

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

# стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    start_string = 'Приветствую! Я бот для быстрого онлайн заказа кофе. Выберите свою роль:'

    bot.send_message(message.chat.id, start_string)


bot.polling(none_stop=True)