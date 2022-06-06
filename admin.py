import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

users_list = [
    {'id': 0, 'role': 'Администратор'},
    {'id': 1, 'role': 'Пользователь'},
    {'id': 2, 'role': 'Бариста'}
]

menu = [
    {'id': 0, 'name': 'Капучино', 'price': 75}
]
name = ''
price = 0

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

# команда для добавления элемента в меню
@bot.message_handler(commands=['add'])
def add(message):
    bot.send_message(message.chat.id, 'Введите название')
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    global name

    if len(message.text) < 3 or len(message.text) > 30:
        bot.send_message(message.chat.id, 'Введите название корректно')
        bot.register_next_step_handler(message, get_name)
    else:
        name = message.text.title()
        bot.send_message(message.chat.id, 'Введите цену')
        bot.register_next_step_handler(message, get_price)

def edit_name(message, idx):
    if len(message.text) < 3 or len(message.text) > 30:
        bot.send_message(message.chat.id, 'Введите название корректно')
        bot.register_next_step_handler(message, edit_name, idx)
    else:
        menu[idx]["name"] = message.text
        bot.send_message(message.chat.id, 'Изменения сохранены')

def get_price(message):
    global price

    if int(message.text) < 2 or int(message.text) >= 10000:
        bot.send_message(message.chat.id, 'Введите цену корректно')
        bot.register_next_step_handler(message, get_price)
    else:
        price = int(message.text)

        keyboard = types.InlineKeyboardMarkup()

        key_yes = types.InlineKeyboardButton(text='Подтвердить', callback_data='confirm')
        keyboard.add(key_yes)

        key_no = types.InlineKeyboardButton(text='Отменить', callback_data='cancel')
        keyboard.add(key_no)

        item_string = f'Название: {name}\nЦена: {price}рублей\n\nВсе правильно?'
        bot.send_message(message.chat.id, item_string, reply_markup=keyboard)

def edit_price(message, idx):
    if int(message.text) < 2 or int(message.text) >= 10000:
        bot.send_message(message.chat.id, 'Введите цену корректно')
        bot.register_next_step_handler(message, edit_price, idx)
    else:
        menu[idx]["price"] = int(message.text)
        bot.send_message(message.chat.id, 'Изменения сохранены')

def convert_role_id_to_string(role_id):
    if role_id == 1:
        return 'Администратор'
    elif role_id == 2:
        return 'Бариста'
    elif role_id == 3:
        return 'Пользователь'

@bot.message_handler(commands=['users'])
def users(message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    query = 'select userId, roleId from users'
    users_list = cursor.execute(query).fetchall()
    users_string = ''

    for user in users_list:
        users_string += f'Id: {user[0]} | Роль: {convert_role_id_to_string(int(user[1]))}\n'

    bot.send_message(message.chat.id, users_string)

@bot.message_handler(commands=['user'])
def user(message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    id = int(message.text.split()[1])

    query = f'select userId, roleId from users where userId = {id}'

    this_user = cursor.execute(query).fetchone()

    if this_user == None:
        bot.send_message(message.chat.id, f'Пользователь с id = {id} не найден')
    else:
        role = convert_role_id_to_string(int(this_user[1]))

        keyboard = types.InlineKeyboardMarkup()

        if role != 'Администратор':
            key_admin = types.InlineKeyboardButton(text='Назначить администратором', callback_data=f'admin {id}')
            keyboard.add(key_admin)
        if role != 'Бариста':
            key_barista = types.InlineKeyboardButton(text='Назначить баристой', callback_data=f'barista {id}')
            keyboard.add(key_barista)
        if role != 'Пользователь':
            key_user = types.InlineKeyboardButton(text='Назначить пользователем', callback_data=f'user {id}')
            keyboard.add(key_user)

        bot.send_message(message.chat.id, f'Роль пользователя: {role}', reply_markup=keyboard)

@bot.message_handler()
def commands(message):
    id = int(message.text[1:])

    idx = -1
    this_item = None

    for i, item in enumerate(menu):
        if item['id'] == id:
            idx = i
            this_item = item
            break

    if idx == -1:
        bot.send_message(message.chat.id, f'Заказ с id = {id} не найден')
    else:
        keyboard = types.InlineKeyboardMarkup()

        key_edit = types.InlineKeyboardButton(text='Изменить', callback_data=f'edit {idx}')
        keyboard.add(key_edit)

        key_delete = types.InlineKeyboardButton(text='Удалить', callback_data=f'delete {idx}')
        keyboard.add(key_delete)

        this_item_string = f'Название: {this_item["name"]} | Цена: {this_item["price"]}'
        bot.send_message(message.chat.id, this_item_string, reply_markup=keyboard)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    callback_data = call.data.split()

    if callback_data[0] == 'confirm':
        global name, price

        item = {
            'id': menu[-1]['id'] + 1,
            'name': name,
            'price': price
        }
        menu.append(item)

        bot.send_message(call.message.chat.id, f'{name} добавлен в меню')

        name = ''
        price = 0

    elif callback_data[0] == 'cancel':
        name = ''
        price = 0
        bot.send_message(call.message.chat.id, 'Операция отменена')

    elif callback_data[0] == 'delete':
        menu.pop(int(callback_data[1]))
        bot.send_message(call.message.chat.id, 'Элемент удален')

    elif callback_data[0] == 'edit':
        idx = int(callback_data[1])
        keyboard = types.InlineKeyboardMarkup()

        key_edit_name = types.InlineKeyboardButton(text='Изменить название', callback_data=f'edit_name {idx}')
        keyboard.add(key_edit_name)

        key_edit_price = types.InlineKeyboardButton(text='Именить цену', callback_data=f'edit_price {idx}')
        keyboard.add(key_edit_price)

        bot.send_message(call.message.chat.id, 'Что вы хотите изменить?', reply_markup=keyboard)

    elif callback_data[0] == 'edit_name':
        bot.send_message(call.message.chat.id, 'Введите название')
        bot.register_next_step_handler(call.message, edit_name, int(callback_data[1]))

    elif callback_data[0] == 'edit_price':
        bot.send_message(call.message.chat.id, 'Введите цену')
        bot.register_next_step_handler(call.message, edit_price, int(callback_data[1]))

    elif callback_data[0] == 'admin':
        query = f'update users set roleId = 1 where userId = {callback_data[1]}'
        cursor.execute(query)
        bot.send_message(call.message.chat.id, 'Роль изменена')
        conn.commit()

    elif callback_data[0] == 'barista':
        query = f'update users set roleId = 2 where userId = {callback_data[1]}'
        cursor.execute(query)
        bot.send_message(call.message.chat.id, 'Роль изменена')
        conn.commit()

    elif callback_data[0] == 'user':
        query = f'update users set roleId = 3 where userId = {callback_data[1]}'
        cursor.execute(query)
        bot.send_message(call.message.chat.id, 'Роль изменена')
        conn.commit()

    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)