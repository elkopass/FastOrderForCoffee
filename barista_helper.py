import sqlite3


def check_if_barista(bot, message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    user_id = message.from_user.id
    query = f'select roleId from users where userId = {user_id}'
    role_id = int(cursor.execute(query).fetchone()[0])

    if role_id == None or role_id > 2:
        error_message = 'Отказано в доступе! Вы не являетесь баристой.'
        bot.send_message(message.chat.id, error_message)
        return False
    else:
<<<<<<< HEAD
        return True
=======
        return True

def convert_orders_list_to_string(orders_list):
    orders_string = ''

    # сначала идут старые заказы
    sorted_orders_list = sorted(orders_list, key=lambda order: order[4], reverse=False)

    # убираем завершенные заказы
    filtered_orders_list = [order for order in sorted_orders_list if order[3] != 3]

    # получаем список уникальных кодов
    orders_by_code = []
    for tmp in filtered_orders_list:
        if tmp[5] not in orders_by_code:
            orders_by_code.append(tmp[5])

    for orders in orders_by_code:
        # записываем одинаковые заказы в один список
        same_order = [o for o in filtered_orders_list if o[5] == orders]

        # достаем список названий элементов из одного заказа
        coffee_list = []
        for order in same_order:
            coffee_list.append(order[7])

        # # формируем отформатированный список
        orders_string += f'/{same_order[0][5]} | Кофе: {", ".join(coffee_list)} ' \
                         f'| Время: {same_order[0][4]} | Статус: {convert_status(same_order[0][3])}\n'

    return orders_string

def convert_order_to_string(order):
    # если заказа с данным кодом не существует, возвращаем None
    if len(order) == 0:
        return None, None

    # достаем список названий элементов из заказа
    names_list = [{'id': order[2], 'name': order[7], 'add': order[8], 'size': order[6], 'price': order[-3],
                   'add_price': order[-2]} for order in order]

    ids = set([t['id'] for t in names_list])

    coffee_and_add = ''
    total_price = 0

    for i in ids:
        curr = ''
        size = 1
        for t in names_list:
            if i == t['id']:
                if curr == '':
                    curr += f'Кофе: {t["name"]} | Добавки: '
                    size = convert_size(t["size"])
                    total_price += t['price']
                if t["add"] == None:
                    curr += 'Нет '
                    total_price += 0
                else:
                    curr += f'{t["add"]} '
                    total_price += t['add_price']

        coffee_and_add += curr + f'| Размер: {size}' + '\n'

    order_string = f'Содержимое заказа\n{coffee_and_add}\nВремя: {order[0][4]}\nСтатус: {convert_status(order[0][3])}\nРейтинг клиента: {order[0][-1]}\nЦена: {total_price} руб.\nКод: {order[0][5]}'

    return order_string, order[0][3]

def convert_status(status):
    if status == 0:
        return 'Новый'
    elif status == 1:
        return 'В процессе'
    elif status == 2:
        return 'Ожидание'
    else:
        return 'Завершен'

def convert_size(size):
    if size == 0:
        return 'Маленький'
    if size == 1:
        return 'Средний'
    else:
        return 'Большой'
>>>>>>> origin/dev
