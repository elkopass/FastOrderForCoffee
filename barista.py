import telebot
from telebot import types
import sqlite3
import emoji
from config import tokens
from barista_helper import check_if_barista
from barista_helper import convert_orders_list_to_string
from barista_helper import convert_order_to_string

bot = telebot.TeleBot(tokens['barista_token'])
orders_list = []

# команда-помощник
@bot.message_handler(commands=['start', 'help'])
def help(message):
    if not check_if_barista(bot, message):
        return

    help_string = 'Это бот для баристы, который позволит Вам работать с заказами.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/orders - получить список активных заказов\n' \
                  '/?  (? - код заказа) - получить заказ по его коду'

    bot.send_message(message.chat.id, help_string, parse_mode='html')

# команда для получения списка заказов
@bot.message_handler(commands=['orders'])
def orders(message):
    if not check_if_barista(bot, message):
        return

    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    # Ниже запросы, за которые меня убил бы Бабанов
    query_not_addition = '''
    select D.id, D.userId, D.pos_id, D.status, D.time, D.code, D.size, D.name, D.add_id  as 'add_name', D.price from 
	(select * from orders 
	join pos_ord on orders.id = pos_ord.ord_id
	join positions on pos_ord.pos_id = positions.id
	join drink_add on pos_ord.pos_id = drink_add.pos_id
	join menu on drink_id = menu.id) as D
	where D.add_id is null
    '''

    query_addition = '''
    select D.id, D.userId, D.pos_id, D.status, D.time, D.code, D.size, D.name, menu.name as 'add_name', D.price from 
	(select * from orders 
	join pos_ord on orders.id = pos_ord.ord_id
	join positions on pos_ord.pos_id = positions.id
	join drink_add on pos_ord.pos_id = drink_add.pos_id
	join menu on drink_id = menu.id) as D
	join menu on add_id = menu.id
    '''

    orders_list = cursor.execute(query_not_addition).fetchall()
    orders_list.extend(cursor.execute(query_addition).fetchall())

    orders_list_string = convert_orders_list_to_string(orders_list)

    if orders_list_string != '':
        bot.send_message(message.chat.id, orders_list_string)
    else:
        bot.send_message(message.chat.id, 'Нет активных заказов')

# команда для полученя заказа по его коду
@bot.message_handler()
def order(message):
    if not check_if_barista(bot, message):
        return

    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    try:
        order_code = int(message.text[1:])

        query_not_addition = f'''
        select D.id, D.userId, D.pos_id, D.status, D.time, D.code, D.size, D.name, D.add_id as 'add_name', D.price, D.add_id as 'add_price', D.rating from 
	    (select * from orders 
	    join pos_ord on orders.id = pos_ord.ord_id
	    join positions on pos_ord.pos_id = positions.id
	    join drink_add on pos_ord.pos_id = drink_add.pos_id
	    join menu on drink_id = menu.id
	    join users on orders.userId = users.id) as D
	    where D.add_id is null and D.code = {order_code}
        '''

        query_addition = f'''
        select D.id, D.userId, D.pos_id, D.status, D.time, D.code, D.size, D.name, menu.name as 'add_name', D.price, menu.price as 'add_price', D.rating from 
	    (select * from orders 
	    join pos_ord on orders.id = pos_ord.ord_id
	    join positions on pos_ord.pos_id = positions.id
	    join drink_add on pos_ord.pos_id = drink_add.pos_id
	    join menu on drink_id = menu.id
	    join users on orders.userId = users.id) as D
	    join menu on add_id = menu.id and D.code = {order_code}
        '''

        this_order = cursor.execute(query_not_addition).fetchall()
        this_order.extend(cursor.execute(query_addition).fetchall())

        order_string, status = convert_order_to_string(this_order)

        if order_string == None:
            error_string = f'Заказ с кодом {order_code} не найден'
            bot.send_message(message.chat.id, error_string)
        else:
            keyboard = types.InlineKeyboardMarkup()

            if status == 0:
                key = types.InlineKeyboardButton(text='В процессе', callback_data=f'in_process {order_code}')
            elif status == 1:
                key = types.InlineKeyboardButton(text='Ожидание', callback_data=f'waiting {order_code}')
            elif status == 2:
                key = types.InlineKeyboardButton(text='Завершен', callback_data=f'completed {order_code}')

            try:
                keyboard.add(key)
                bot.send_message(message.chat.id, order_string, reply_markup=keyboard)
            except:
                bot.send_message(message.chat.id, order_string)
    except:
        error_string = f'Команда {message.text} не найдена. ' \
                       f'Обратитесь к /help, чтобы получить список доступных команд'
        bot.send_message(message.chat.id, error_string)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    callback_data = call.data.split()

    state = callback_data[0]
    order_code = int(callback_data[1])

    state_db = state

    if state == "in_process":
        state_db = 1
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} в процессе')

    elif state == "waiting":
        state_db = 2
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} завершен и ждет получателя')

    elif state == "completed":
        state_db = 3
        keyboard = types.InlineKeyboardMarkup()

        rate_client_5 = types.InlineKeyboardButton(text=emoji.emojize(':star:' * 5),
                                                   callback_data=f'rate {order_code} {5}')
        rate_client_4 = types.InlineKeyboardButton(text=emoji.emojize(':star:' * 4),
                                                   callback_data=f'rate {order_code} {4}')
        rate_client_3 = types.InlineKeyboardButton(text=emoji.emojize(':star:' * 3),
                                                   callback_data=f'rate {order_code} {3}')
        rate_client_2 = types.InlineKeyboardButton(text=emoji.emojize(':star:' * 2),
                                                   callback_data=f'rate {order_code} {2}')
        rate_client_1 = types.InlineKeyboardButton(text=emoji.emojize(':star:' * 1),
                                                   callback_data=f'rate {order_code} {1}')

        keyboard.add(rate_client_5)
        keyboard.add(rate_client_4)
        keyboard.add(rate_client_3)
        keyboard.add(rate_client_2)
        keyboard.add(rate_client_1)

        bot.send_message(call.message.chat.id, f'Заказ /{order_code} получен. Оцените клиента', reply_markup=keyboard)

    elif state == 'rate':
        bot.send_message(call.message.chat.id, f'Вы оценили заказ /{order_code} на {callback_data[2]} звезд. Спасибо!')

    if state != 'rate':
        query = f'update orders set status = {state_db} where code = {order_code}'
        cursor.execute(query)
    else:
        stars = int(callback_data[2])
        query_get_user = f'select userId from orders where code = {int(order_code)}'
        user_id = cursor.execute(query_get_user).fetchone()[0]
        query_user_rating = f'select rating from users where id = {user_id}'
        rating = cursor.execute(query_user_rating).fetchone()[0]

        updated_rating = float(f"{(rating + stars) / 2:.{1}f}")
        query = f'update users set rating = {updated_rating} where id = {user_id}'

        cursor.execute(query)

    bot.answer_callback_query(call.id)
    conn.commit()

bot.polling(none_stop=True)