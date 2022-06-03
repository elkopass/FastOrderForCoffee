import telebot
from telebot import types

bot = telebot.TeleBot('5240548361:AAEbvuwJy3-ErEJ3WeepU8zsYOUdw0u3dHw')

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

def get_price(message):
    global price

    if int(message.text) < 2 or int(message.text) >= 10000:
        bot.send_message(message.chat.id, 'Введите цену корректно')
        bot.register_next_step_handler(message, get_price)
    else:
        price = message.text

        keyboard = types.InlineKeyboardMarkup()

        key_yes = types.InlineKeyboardButton(text='Подтвердить', callback_data='confirm')
        keyboard.add(key_yes)

        key_no = types.InlineKeyboardButton(text='Отменить', callback_data='cancel')
        keyboard.add(key_no)

        item_string = f'Название: {name}\nЦена: {price}рублей\n\nВсе правильно?'
        bot.send_message(message.chat.id, item_string, reply_markup=keyboard)

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'confirm':
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
    elif call.data == 'cancel':
        name = ''
        price = 0
        bot.send_message(call.message.chat.id, 'Операция отменена')

    bot.answer_callback_query(call.id)

bot.polling(none_stop=True)