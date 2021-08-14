# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:12:35 2021

@author: agent2k
"""
import csv
from datetime import datetime
import os
import pandas as pd
import inspect
import telebot as tb
import tempfile

users_type = {
    1: 'пользователь',
    2: 'пользователя',
    3: 'пользователя',
    4: 'пользователя'
}
day_type = {
    1: 'день',
    2: 'дня',
    3: 'дня',
    4: 'дня'
}

dict_stat = dict()

btn_menu = ['Получить статистику',
            'Очистить всю статистику',
            'Скачать статистику csv',
            'Скачать базу языков csv',
            'Помощь',
            'Выход']
key_menu = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
key_menu.add(*btn_menu)

bot = ''
password = ''
markup_remove = ''

# remove txt file
def remove(user_id):
    path = os.getcwd() + f'/{user_id}.txt'
    os.remove(path)


# write data to csv
def statistics(user_id, command=None):
    date = datetime.today().strftime("%d.%m.%Y")
    replace = False
    quantity = 1

    file_name = path_dir('data.csv')
    df = pd.read_csv(file_name, delimiter=';', encoding='cp1251')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.sort_values('date')
    df['date'] = df['date'].dt.strftime("%d.%m.%Y")

    remove_period = 180
    days = df['date'].unique()
    if date not in days:
        remove_period -= 1

    if len(days) > remove_period:
        index = 0
        nb = ''
        for i in reversed(days):
            if index >= remove_period:
                break
            f_id = df['date'] == i
            if len(nb) > 0:
                nb = pd.concat([df.loc[f_id], nb])
            else:
                nb = df.loc[f_id]

            index += 1
        replace = True
        df = nb

    f_id = (df['date'] == date) & (df['id'] == user_id)
    base = df.loc[f_id]
    f_id = base['command'] == command
    base = base.loc[f_id]

    if len(base) == 1:
        quantity = int(df.loc[base.index, 'quantity'])
        df.loc[base.index, 'quantity'] = quantity + 1
        df.to_csv(file_name, sep=';', encoding='cp1251', index=False)
    elif replace:
        d = {
            'date': [date],
            'id': [user_id],
            'command': [command],
            'quantity': [quantity]
            }
        nb = pd.DataFrame(data=d)
        df = pd.concat([df, nb])
        df.to_csv(file_name, sep=';', encoding='cp1251', index=False)
    else:
        with open(file_name, 'a', newline="", encoding='cp1251') \
            as file:
            wr = csv.writer(file, delimiter=';')
            wr.writerow([date, user_id, command, quantity])


#getting the path to the script
def path_dir(name):
    path = inspect.getabsfile(path_dir)
    path = os.path.realpath(path)
    path = os.path.join(os.path.dirname(path), name)
    return path


def clear_statistics():
    d = {
        'date': [],
        'id': [],
        'command': [],
        'quantity': []
        }
    df = pd.DataFrame(data=d)
    file_name = path_dir('data.csv')
    df.to_csv(file_name, sep=';', encoding='cp1251', index=False)


# make report
def analysis(message):
    period = message['period']

    df = pd.read_csv(path_dir('data.csv'), delimiter=';', encoding='cp1251')

    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.sort_values('date')

    q_days = len(df['date'].unique())
    q_users = len(df['id'].unique())

    days_s =  day_type.get(period, 'дней')
    days_sq =  day_type.get(q_days, 'дней')

    m_out = f'Всего статистика собрана за {q_days} {days_sq} \n'

    if period > q_days:
        period = q_days
        m_out += 'Указанное вами количество дней больше, чем имеется.\n' \
                 'Будет выведена статистика за максимальное возможное время.\n'

    m_out += f'Статистика использования бота за {period} {days_s}: \n'

    if 'users' in message['agg']:
        m_users = users_type.get(q_users, 'пользователей')
        m_out += f'\nЗа всё время бота использовало {q_users} {m_users}\n' \
                 f'Статистика пользователей за последние {period} {days_s}: \n'

        base = df.groupby('date')
        index = 0

        for i in reversed(base.groups):
            if index >= period:
                break

            filter_id = df['date'] < i
            users_old = df['id'].loc[filter_id].unique().tolist()
            q_users_new = 0

            date = pd.to_datetime(str(i)).strftime('%d.%m.%Y')
            q_date_users = []

            for j in base.groups[i]:
                if df['id'][j] not in q_date_users:
                    q_date_users.append(df['id'][j])
                if df['id'][j] not in users_old:
                    q_users_new +=1
                    users_old.append(df['id'][j])

            q_date_users = len(q_date_users)
            m_out += f'дата: {date} пользователей {q_date_users} ' \
                     f'из них новых пользователей {q_users_new}\n'
            index += 1

    if 'commands' in message['agg']:
        m_out += f'\nСтатистика команд за последние {period} {days_s}: \n'

        base = df.groupby('date')
        index = 0

        for i in reversed(base.groups):
            if index >= period:
                break

            date = pd.to_datetime(str(i)).strftime('%d.%m.%Y')
            m_out += f'дата: {date} '  \

            filter_id = df['date'] == i
            commads = df.loc[filter_id]
            commads = commads.groupby('command')
            commads = commads['quantity'].sum().reset_index()

            q_sum = commads['quantity'].sum()
            m_out += f'Всего команд за день {q_sum}:\n'

            for j in range(len(commads)):
                commad = commads['command'][j]
                q_commad = commads['quantity'][j]
                m_out += f'команда: {commad} - использовали {q_commad} раз\n'

            index += 1

    return m_out

#основное меню статистики
def get_statistics(message, bot_id, remove, access):
    global bot, markup_remove, password

    bot = bot_id
    markup_remove = remove
    password = access

    mes_id = message.from_user.id
    text_out = 'Введите пароль доступа для возврата к боту \выход:\n'
    bot.send_message(mes_id, text=text_out)
    bot.register_next_step_handler(message, check_password)

def check_password(message):
    mes_id = message.chat.id
    message_user = message.text

    if message_user == password:
        text_out = 'Меню статистики.\nВыберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)
    elif message_user.lower() == '\выход':
        text_out = 'Вы вышли из статистики.\n'
        bot.send_message(mes_id, text=text_out)
    else:
        text_out = 'Введен не верный пароль.\n' \
                   'Введите пароль доступа для возврата к боту \выход:\n'
        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, check_password)


def statistics_menu_answer(message):
    mes_id = message.from_user.id
    message_user = message.text

    if message_user == 'Получить статистику':
        statistics_step(message)

    elif message_user == 'Очистить всю статистику':
        clear_statistics()
        text_out = 'Статистика успешно очищена.\n'
        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, statistics_menu_answer)

    elif message_user == 'Скачать статистику csv':
        file_name = path_dir('data.csv')
        with open(file_name, "rb") as file:
            bot.send_document(mes_id,file)
        bot.register_next_step_handler(message, statistics_menu_answer)

    elif message_user == 'Скачать базу языков csv':
        file_name = 'base/lang_base.csv'
        with open(file_name, "rb") as file:
            bot.send_document(mes_id,file)
        bot.register_next_step_handler(message, statistics_menu_answer)

    elif message_user == 'Помощь':
        with open(path_dir('help.txt'), 'r', encoding="utf-8") as text:
            text_out = text.read()

        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, statistics_menu_answer)

    elif message_user == 'Выход':
        text_out = 'Вы вышли из статистики.\nЯ Вас внимательно слушаю\n'
        bot.send_message(mes_id, text=text_out, reply_markup=markup_remove)

    else:
        text_out = 'Я Вас не понимаю. Пожалуйста повторите выбор:\n'
        bot.register_next_step_handler(message, statistics_menu_answer)

#получение статистики по шагам
def statistics_step(message):
    dict_stat = dict()

    mes_id = message.from_user.id
    text_out = 'За какое количество дней Вы хотите получить ' \
               'статистику (введите число или \отмена для возврата в меню):\n'
    bot.send_message(mes_id, text=text_out, reply_markup=markup_remove)
    bot.register_next_step_handler(message, statistics_step1, dict_stat)


def statistics_step1(message, dict_stat):
    message_user = message.text
    mes_id = message.from_user.id

    btn_stat = ['Пользователи',
                'Комманды',
                'Пользователи и команды',
                'Отмена']
    key_stat = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    key_stat.add(*btn_stat)

    if message_user.lower() == '\отмена':
        text_out = 'Вы вышли в меню статистики.\n' \
                   'Выберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)
    elif message_user.isdigit():
        dict_stat['period'] = int(message_user)
        text_out = 'Выберите вариант получения статистики:\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_stat)
        bot.register_next_step_handler(message, statistics_step2, dict_stat)
    else:
        text_out = 'Я Вас не понимаю. Пожалуйста введите число дней:\n'
        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, statistics_step1, dict_stat)


def statistics_step2(message, dict_stat):
    message_user = message.text
    mes_id = message.from_user.id

    if message_user == 'Пользователи':
        dict_stat['agg'] = ['users']
    elif message_user == 'Комманды':
        dict_stat['agg'] = ['commands']
    elif message_user == 'Пользователи и команды':
        dict_stat['agg'] = ['users','commands']
    elif message_user == 'Отмена':
        text_out = 'Вы вышли в меню статистики.\n'
        bot.send_message(mes_id, text=text_out, reply_markup=markup_remove)
        text_out = 'Выберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)
    else:
        text_out = 'Я Вас не понимаю. Пожалуйста повторите выбор:\n'
        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, statistics_step2, dict_stat)


    btn_out = ['На экран', 'В файл', 'Отмена']
    btn_file = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_file.add(*btn_out)

    text_out = 'Выберите способ отображения статистики.\n'
    bot.send_message(mes_id, text=text_out, reply_markup=btn_file)
    bot.register_next_step_handler(message, statistics_step3, dict_stat)

def statistics_step3(message, dict_stat):
    mes_id = message.from_user.id
    message_user = message.text

    if message_user == 'На экран':
        result = analysis(dict_stat)
        bot.send_message(mes_id, text=result, reply_markup=markup_remove)

        text_out = 'Статистика получена.\nВыберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)

    elif message_user == 'В файл':
        date = datetime.today().strftime('%d-%m-%Y-%H_%M_%S')
        results = analysis(dict_stat)
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8' ) as fp:
            fp.name = date + '.txt'
            fp.write(results)
            fp.seek(0)
            bot.send_document(mes_id,fp)
            fp.close()

        text_out = 'Статистика получена.\n'
        bot.send_message(mes_id, text=text_out, reply_markup=markup_remove)
        text_out = 'Выберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)


    elif message_user == 'Отмена':
        text_out = 'Вы вышли в меню статистики.\n'
        bot.send_message(mes_id, text=text_out, reply_markup=markup_remove)
        text_out = 'Выберите необходимое действие\n'
        bot.send_message(mes_id, text=text_out, reply_markup=key_menu)
        bot.register_next_step_handler(message, statistics_menu_answer)

    else:
        text_out = 'Я Вас не понимаю. Пожалуйста повторите выбор:\n'
        bot.send_message(mes_id, text=text_out)
        bot.register_next_step_handler(message, statistics_step3, dict_stat)