import telebot
from telebot import types
import sqlite3
from config import tokens
from admin_helper import check_if_admin
<<<<<<< HEAD
=======
from admin_helper import convert_role_id_to_string
from admin_helper import convert_type_id_to_string
>>>>>>> origin/dev

bot = telebot.TeleBot(tokens['admin_token'])
users_list = []

menu = []
name = ''
price = 0
<<<<<<< HEAD
=======
type = 0
>>>>>>> origin/dev

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
        conn = sqlite3.connect('sqlite3.db')
        cursor = conn.cursor()
        query = f'update menu set name = "{message.text}" where id = {idx}'
        cursor.execute(query)
        bot.send_message(message.chat.id, 'Изменения сохранены')
        conn.commit()

def get_price(message):
    global price, type

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

        type_text = 'Напиток'
        if type == 1:
            type_text = 'Добавка'

        item_string = f'Тип: {type_text}\nНазвание: {name}\nЦена: {price} руб.\n\nВсе правильно?'
        bot.send_message(message.chat.id, item_string, reply_markup=keyboard)

def edit_price(message, idx):
    if int(message.text) < 2 or int(message.text) >= 10000:
        bot.send_message(message.chat.id, 'Введите цену корректно')
        bot.register_next_step_handler(message, edit_price, idx)
    else:
        conn = sqlite3.connect('sqlite3.db')
        cursor = conn.cursor()
        query = f'update menu set price = {int(message.text)} where id = {idx}'
        cursor.execute(query)
        bot.send_message(message.chat.id, 'Изменения сохранены')
        conn.commit()


# команда-помощник
@bot.message_handler(commands=['start', 'help'])
def help(message):
    if not check_if_admin(bot, message):
        return

    help_string = 'Это бот для администратора, который позволит Вам работать с системой.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/menu - получить список всех элементов меню\n' \
                  '/add - добавить элемент в меню\n' \
                  '/?  (? - id элемента) - получить элемент меню по его идентификатору\n' \
                  '/users - получить список пользователей\n' \
                  '/user ? (? - id пользователя) - получить пользователя по его идентификатору'

    bot.send_message(message.chat.id, help_string, parse_mode='html')

# команда для получения всех элементов меню
@bot.message_handler(commands=['menu'])
def menu(message):
    if not check_if_admin(bot, message):
        return

    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    query = 'select * from menu'
    menu = cursor.execute(query).fetchall()
    menu_string = ''

    for item in menu:
        menu_string += f'/{item[0]} | Категория: {convert_type_id_to_string(item[-1])} ' \
                       f'| Название: {item[1]} | Цена: {item[2]} руб.\n'

    if menu_string == '':
        menu_string = 'В меню нет элементов'

    bot.send_message(message.chat.id, menu_string)

# команда для добавления элемента в меню
@bot.message_handler(commands=['add'])
def add(message):
    if not check_if_admin(bot, message):
        return

    keyboard = types.InlineKeyboardMarkup()

    key_drink = types.InlineKeyboardButton(text='Напиток', callback_data=f'type {0}')
    keyboard.add(key_drink)

    key_add = types.InlineKeyboardButton(text='Добавка', callback_data=f'type {1}')
    keyboard.add(key_add)

    bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=keyboard)

@bot.message_handler(commands=['users'])
def users(message):
    if not check_if_admin(bot, message):
        return

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
    if not check_if_admin(bot, message):
        return

    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    try:
        id = int(message.text.split()[1])
    except:
        bot.send_message(message.chat.id, 'Введите id пользователя')
        return

    query = f'select userId, roleId from users where userId = {id}'
    this_user = cursor.execute(query).fetchone()

    if this_user == None:
        bot.send_message(message.chat.id, f'Пользователь с id {id} не найден')
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
    if not check_if_admin(bot, message):
        return

    try:
        id = int(message.text[1:])

        conn = sqlite3.connect('sqlite3.db')
        cursor = conn.cursor()

        query = f'select name, price from menu where id = {id}'
        this_item = cursor.execute(query).fetchone()

        if this_item == None:
            bot.send_message(message.chat.id, f'Заказ с id = {id} не найден')
        else:
            keyboard = types.InlineKeyboardMarkup()

            key_edit = types.InlineKeyboardButton(text='Изменить', callback_data=f'edit {id}')
            keyboard.add(key_edit)

            key_delete = types.InlineKeyboardButton(text='Удалить', callback_data=f'delete {id}')
            keyboard.add(key_delete)

            this_item_string = f'Название: {this_item[0]} | Цена: {this_item[1]}'
            bot.send_message(message.chat.id, this_item_string, reply_markup=keyboard)
    except:
        error_string = f'Команда {message.text} не найдена. ' \
                       f'Обратитесь к /help, чтобы получить список доступных команд'
        bot.send_message(message.chat.id, error_string)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global name, price, type
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    callback_data = call.data.split()

    if callback_data[0] == 'type':
        type = int(callback_data[1])
        bot.send_message(call.message.chat.id, 'Введите название')
        bot.register_next_step_handler(call.message, get_name)

    elif callback_data[0] == 'confirm':
        query = f'insert into menu (name, price, type) values ("{name}", {price}, {type})'

        cursor.execute(query)

        bot.send_message(call.message.chat.id, f'{name} добавлен в меню')

        name = ''
        price = 0

        conn.commit()

    elif callback_data[0] == 'cancel':
        name = ''
        price = 0
        type = 0
        bot.send_message(call.message.chat.id, 'Операция отменена')

    elif callback_data[0] == 'delete':
        query = f'delete from menu where id = {int(callback_data[1])}'
        cursor.execute(query)

        bot.send_message(call.message.chat.id, 'Элемент удален')
        conn.commit()

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