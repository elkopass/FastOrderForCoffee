import telebot
from telebot import types
import sqlite3
from user import user

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

your_profile = ()

def convert_role_id_to_string_for_error(role_id):
    if role_id == 2:
        return 'баристой'
    elif role_id == 1:
        return 'администратором'

def chose_role(message, message_text):
    keyboard = types.InlineKeyboardMarkup()

    key_admin = types.InlineKeyboardButton(text='Администратор', callback_data='1')
    keyboard.add(key_admin)

    key_barista = types.InlineKeyboardButton(text='Бариста', callback_data='2')
    keyboard.add(key_barista)

    key_user = types.InlineKeyboardButton(text='Пользователь', callback_data='3')
    keyboard.add(key_user)

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard)

# стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    start_string = 'Приветствую! Я бот для быстрого онлайн заказа кофе. Выберите свою роль:'

    chose_role(message, start_string)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()
    your_id = call.from_user.id

    callback_data = call.data.split()

    query = f'select roleId from users where userId = {your_id}'
    your_role = cursor.execute(query).fetchone()[0]

    if int(callback_data[0]) < int(your_role):
        error_string = f'Вы не являетесь {convert_role_id_to_string_for_error(int(callback_data[0]))}\n' \
                       f'Выберите правильную роль'

        chose_role(call.message, error_string)

    else:
        your_profile = user(int(callback_data[0]))
        ok_string= f'Вы выбрали роль <strong>{your_profile.get_role_string()}</strong> \n\n' \
                    f'Введите команду /help, чтобы обратиться к доступному функионалу'
        bot.send_message(call.message.chat.id, ok_string, parse_mode='html')


bot.polling(none_stop=True)