import telebot
from telebot import types
import sqlite3
from sqlite3 import Error

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

orders_list = []


def convert_orders_list_to_string(orders_list):
    orders_string = ''

    # сначала идут новые заказы
    sorted_orders_list = sorted(orders_list, key=lambda order: order[-1], reverse=True)

    # убираем завершенные заказы
    filtered_orders_list = [order for order in sorted_orders_list if order[-2] != 'completed']

    # получаем список уникальных кодов
    orders_by_code = list(set([x[0] for x in filtered_orders_list]))

    for orders in orders_by_code:
        # записываем одинаковые заказы в один список
        same_order = [o for o in filtered_orders_list if o[0] == orders]

        # достаем список названий элементов из одного заказа
        names_list = []
        for order in same_order:
            names_list.append(order[2])

        # формируем отформатированный список
        orders_string += f'/{same_order[0][0]} | Заказ: {", ".join(names_list)} ' \
                         f'| Время: {same_order[0][-1]} | Статус: {convert_status(same_order[0][-2])}\n'

    return orders_string

def convert_order_to_string(order):
    # если заказа с данным кодом не существует, возвращаем None
    if len(order) == 0:
        return None, None

    # достаем список названий элементов из заказа
    names_list = [order[2] for order in order]

    order_string = f'Заказ: {", ".join(names_list)} | Время: {order[0][-2]} ' \
                   f'| Статус: {convert_status(order[0][-3])} | Рейтинг клиента: {order[0][-1]}\n'

    return order_string, order[0][-2]

def convert_status(status):
    if status == 'new':
        return 'Новый'
    elif status == 'in process':
        return 'В процессе'
    elif status == 'waiting':
        return 'Ожидание'
    else:
        return 'Завершен'


# команда-помощник
@bot.message_handler(commands=['help'])
def help(message):
    help_string = 'Это бот для баристы, который позволит Вам работать с заказами.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/orders - получить список активных заказов\n' \
                  '/?  (? - код заказа) - получить заказ по его коду'

    bot.send_message(message.chat.id, help_string, parse_mode='html')

# команда для получения списка заказов
@bot.message_handler(commands=['orders'])
def orders(message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    query = '''
    select orders.id, userId, name, size, status, time
    from orders join pos_ord
        on pos_ord.ord_id = orders.id
    join positions
        on pos_ord.pos_id = positions.id
    '''
    orders_list = cursor.execute(query).fetchall()
    bot.send_message(message.chat.id, convert_orders_list_to_string(orders_list))

# команда для полученя заказа по его коду
@bot.message_handler()
def order(message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    try:
        order_code = int(message.text[1:])

        query = f'''
                    select orders.id, users.userId, name, size, status, time, rating
                    from orders join pos_ord
                        on pos_ord.ord_id = {order_code} and orders.id = {order_code}
                    join positions
                        on pos_ord.pos_id = positions.id
                    join users 
                    	on users.id = orders.userId
                    '''

        this_order = cursor.execute(query).fetchall()

        order_string, status = convert_order_to_string(this_order)

        if order_string == None:
            error_string = f'Заказ с кодом {order_code} не найден'
            bot.send_message(message.chat.id, error_string)
        else:
            keyboard = types.InlineKeyboardMarkup()

            if status == 'new':
                key = types.InlineKeyboardButton(text='В процессе', callback_data=f'in_process {order_code}')
            elif status == 'in process':
                key = types.InlineKeyboardButton(text='Ожидание', callback_data=f'waiting {order_code}')
            elif status == 'waiting':
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
        state_db = 'in process'
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} в процессе')

    elif state == "waiting":
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} завершен и ждет получателя')

    elif state == "completed":
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} получен')

    query = f'update orders set status = "{state_db}" where id = {order_code}'
    cursor.execute(query)
    conn.commit()

bot.polling(none_stop=True)