import telebot
from telebot import types

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

# команда-помощник
@bot.message_handler(commands=['help'])
def help(message):
    help_string = 'Это бот для администратора, который позволит Вам работать с системой.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/add - добавить элемент в меню\n' \
                  '/?  (? - id элемента) - получить элемент меню по его идентификатору\n' \
                  '/users - получить список пользователей\n' \
                  '/user ? (? - id пользователя) - получить пользователя по его идентификатору'

    bot.send_message(message.chat.id, help_string, parse_mode='html')

bot.polling(none_stop=True)