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

# команда-помощник
@bot.message_handler(commands=['help'])
def help(message):
    help_string = 'Это бот для баристы, который позволит Вам работать с заказами.\n\n' \
                  '<strong>Список команд</strong>\n' \
                  '/orders - получить список активных заказов\n' \
                  '/?  (? - идентификатор заказа) - получить заказ по его идентификатору'

    bot.send_message(message.chat.id, help_string, parse_mode='html')

# команда для получения списка заказов
@bot.message_handler(commands=['orders'])
def orders(message):
    new_orders = ''

    for order in orders_list:
        if order['status'] != 'completed':
            new_orders += f'/{order["code"]} | Кофе: {order["name"]} | Время: {order["time"]} | Статус: {order["status"]}\n'

    bot.send_message(message.chat.id, new_orders)

bot.polling(none_stop=True)