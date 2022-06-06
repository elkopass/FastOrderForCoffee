import telebot
from telebot import types
import sqlite3
from sqlite3 import Error

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

orders_list = [
    {'id': 4, 'code': 73872304, 'name': 'Капучино', 'status': 'new', 'time': '14:30' },
    {'id': 5, 'code': 73872304, 'name': 'Эспрессо', 'status': 'new', 'time': '14:30'},
    {'id': 0, 'code': 89374287, 'name': 'Американо', 'status': 'completed', 'time': '14:15'},
    {'id': 3, 'code': 37593577, 'name': 'Капучино', 'status': 'new', 'time': '14:28'},
    {'id': 1, 'code': 37465027, 'name': 'Латте', 'status': 'in process', 'time': '14:20'},
    {'id': 2, 'code': 37465027, 'name': 'Латте', 'status': 'in process', 'time': '14:20'}
]


def convert_orders_list_to_string(orders_list):
    orders_string = ''

    # сначала идут новые заказы
    sorted_orders_list = sorted(orders_list, key=lambda order: order['time'], reverse=True)

    # убираем завершенные заказы
    filtered_orders_list = [order for order in sorted_orders_list if order['status'] != 'completed']

    # получаем список уникальных кодов
    orders_by_code = list(set([x['code'] for x in filtered_orders_list]))

    for orders in orders_by_code:
        # записываем одинаковые заказы в один список
        same_order = [o for o in filtered_orders_list if o['code'] == orders]

        # достаем список названий элементов из одного заказа
        names_list = []
        for order in same_order:
            names_list.append(order['name'])

        # формируем отформатированный список
        orders_string += f'/{same_order[0]["code"]} | Заказ: {", ".join(names_list)} ' \
                         f'| Время: {same_order[0]["time"]} | Статус: {convert_status(same_order[0]["status"])}\n'

    return orders_string

def convert_order_to_string(order_code):
    # получаем список элементов заказа с соответствующим кодом
    this_items_list = [order for order in orders_list if order["code"] == order_code]

    # если заказа с данным кодом не существует, возвращаем None
    if len(this_items_list) == 0:
        return None

    # достаем список названий элементов из заказа
    names_list = [order["name"] for order in this_items_list]

    order_string = f'Заказ: {", ".join(names_list)} | Время: {this_items_list[0]["time"]} ' \
                   f'| Статус: {convert_status(this_items_list[0]["status"])}\n'

    return order_string, this_items_list[0]["status"]

def change_orders_status(order_code, status):
    for order in orders_list:
        if order["code"] == order_code:
            order["status"] = status

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
    orders_query = cursor.execute(query)
    print(orders_query.fetchall())

    bot.send_message(message.chat.id, convert_orders_list_to_string(orders_list))

# команда для полученя заказа по его коду
@bot.message_handler()
def order(message):
    try:
        order_code = int(message.text[1:])
        order_string, status = convert_order_to_string(order_code)

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
                bot.send_message(message.chat.id, convert_order_to_string(order_code), reply_markup=keyboard)
            except:
                bot.send_message(message.chat.id, convert_order_to_string(order_code))
    except:
        error_string = f'Команда {message.text} не найдена. ' \
                       f'Обратитесь к /help, чтобы получить список доступных команд'
        bot.send_message(message.chat.id, error_string)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    callback_data = call.data.split()

    state = callback_data[0]
    order_code = int(callback_data[1])

    if state == "in_process":
        change_orders_status(order_code, 'in process')
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} в процессе')

    elif state == "waiting":
        change_orders_status(order_code, 'waiting')
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} завершен и ждет получателя')

    elif state == "completed":
        change_orders_status(order_code, 'completed')
        bot.send_message(call.message.chat.id, f'Заказ /{order_code} получен')

bot.polling(none_stop=True)