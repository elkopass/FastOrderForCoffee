import sqlite3


def check_if_admin(bot, message):
    conn = sqlite3.connect('sqlite3.db')
    cursor = conn.cursor()

    user_id = message.from_user.id
    query = f'select roleId from users where userId = {user_id}'
    role_id = int(cursor.execute(query).fetchone()[0])

    if role_id == None or role_id != 1:
        error_message = 'Отказано в доступе! Вы не являетесь администратором.'
        bot.send_message(message.chat.id, error_message)
        return False
    else:
        return True

def convert_role_id_to_string(role_id):
    if role_id == 1:
        return 'Администратор'
    elif role_id == 2:
        return 'Бариста'
    elif role_id == 3:
        return 'Пользователь'