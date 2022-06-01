import telebot
from telebot import types

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

        # достаем список кофе из одного заказа
        coffee_list = []
        for order in same_order:
            coffee_list.append(order['name'])

        # формируем отформатированный список
        orders_string += f'/{same_order[0]["code"]} | Кофе: {", ".join(coffee_list)} ' \
                         f'| Время: {same_order[0]["time"]} | Статус: {convert_status(same_order[0]["status"])}\n'

    return orders_string

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
    bot.send_message(message.chat.id, convert_orders_list_to_string(orders_list))

bot.polling(none_stop=True)