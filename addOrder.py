

# функция для обработки кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):

    state = call.data.split()[0]
    
    if state == "gg":
        bot.answer_callback_query(call.id)
        return
    else:
        bot.delete_message(call.message.chat.id, call.message.id)
        id = int(call.data.split()[1])
        if state == "add":  
            ordersORM[id].append('Kапучино')
            param['Addings'] = []
            param['Size'] = ""
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "rem":
            if (('Kапучино' in ordersORM[id]) == False):
                
                    bot.send_message(id, 'У вас и так нет капучино в заказе')
            else:
                ordersORM[id].remove('Kапучино')
        elif state =="size":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Средний', callback_data= f"med {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Большой', callback_data= f"sml {call.message.chat.id}")
            
            keyboard.add(key1, key2)
            
            bot.send_message(call.message.chat.id, 'Выберите размер:', reply_markup=keyboard)
        elif state == "adding":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Шоколадная крошка', callback_data= f"addings {call.message.chat.id}")
            keyboard.add(key1)
            bot.send_message(call.message.chat.id, 'Выберите добавку:', reply_markup=keyboard)
        elif state == "sml":
            param['Size'] = "Cредний"
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "med":
            param['Size'] = "Большой"
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
           
            
        elif state == "addings":
            param['Addings'].append("Sugar")
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Выбрать размер', callback_data= f"size {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Выбрать добавку', callback_data= f"adding {call.message.chat.id}")
            key3 = types.InlineKeyboardButton(text='Добавить позицию', callback_data= f"sendP {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(key3)
            bot.send_message(call.message.chat.id, 'Детали заказа', reply_markup=keyboard)
        elif state == "sendP":
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='Добавить Капучино', callback_data= f"add {call.message.chat.id}")
            key2 = types.InlineKeyboardButton(text='Убрать Капучино', callback_data= f"rem {call.message.chat.id}")
            item3 = types.InlineKeyboardButton("Посмотреть заказ", callback_data= f"check {call.message.chat.id}")
            item4 = types.InlineKeyboardButton("Отправить заказ", callback_data= f"sendO {call.message.chat.id}")
            keyboard.add(key1, key2)
            keyboard.add(item3, item4)
            
            bot.send_message(call.message.chat.id, 'Выберите позицию:', reply_markup=keyboard)
        elif state == "sendO":  
            msg = bot.send_message(call.message.chat.id, 'Через сколько минут вам хотелось бы забрать кофе')
            bot.register_next_step_handler(msg, start_2)
            
        elif state == "check":
            str1 = ""
            for i in param['Addings']:
                if (i == "Sugar"):
                    str1 +=  "Шоколадная крошка "
            
            bot.send_message(call.message.chat.id, f'Позиции: {ordersORM[id][0]}\n Размер: {param["Size"]} \n Добавки: {str1} ')
            keyboard = types.InlineKeyboardMarkup()
            key1 = types.InlineKeyboardButton(text='ДА', callback_data= f"sendO {call.message.chat.id}")
            keyboard.add(key1)
            bot.send_message(call.message.chat.id, 'Отправить заказ ?', reply_markup=keyboard)
