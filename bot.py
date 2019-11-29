# -*- coding: utf-8 -*-

# import config
import os


import telebot
import sqlite3
import secrets
import datetime
import re
from idlelib import query
from random import shuffle
from datetime import datetime
from telebot import (apihelper, types)
# from config import (token, socks5)
from telebot.types import ReplyKeyboardRemove

from settings import *


apihelper.proxy = {'https': socks5}
bot = telebot.TeleBot(token)
print('сервер работает...')
user = bot.get_me()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        start_param = message.text.split()
        if len(start_param) == 1:
            print('нет параметра запуска')
            bot.send_message(message.chat.id, text='Привет! Я Санта-бот, помогу провести новогодний '
                                                   'розыгрыш подарков в вашей компании!')
            keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура шириной в 2 кнопи в ряду
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_group')
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_group')
            keyboard.add(key_yes, key_no)  # добавляем кнопки в клавиатуру в один ряд
            # keyboard.add(key_no) # добавлять по одной кнопке в ряд
            question = 'Хочешь создать новую группу для розыгрыша?'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            # bot.register_next_step_handler(message, new_group)
        else:
            print('есть параметр запуска:')
            print(start_param[1])
            # проверяем, что такая группа есть в БД и она активна (розыгрыша не было)
            # устанавливаем соединение с БД (объект соединения)
            conn = sqlite3.connect("santa.db")
            # создаем объект Cursor для работы с его методом execute()
            curs = conn.cursor()
            # создаем связь с группой, если она существует иначе ссылка недействительна
            curs.execute('SELECT * FROM Groups WHERE link=:link', {'link': start_param[1]})
            group_exists = curs.fetchall()
            print(f'есть группа: {group_exists}')

            # print(f'статус розыгрыша: raffle = {group_exists[0][3]}') # код падает, т.к группы еще может не быть
            print(f'количество групп: {len(group_exists)}')

            # проверяем, что raffle (group_exists[0][3]) равно 0 (розыгрыша не было)
            if len(group_exists) == 1 and group_exists[0][3] == 0:
                # если пользователя нет в БД, заносим его туда
                conn = sqlite3.connect("santa.db")
                curs = conn.cursor()
                curs.execute('SELECT * FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
                user_exists = curs.fetchall()
                print(f'есть пользователь: {user_exists}')
                print(f'количество пользователей: {len(user_exists)}')

                # если пользователя нет в БД, заносим его туда
                if len(user_exists) == 0:
                    curs.execute('INSERT INTO Users(tg_id, username, first_name, last_name, current_group) '
                                 'VALUES (:tg_id, :username, :first_name, :last_name, :current_group)',
                                 {'tg_id': message.chat.id, 'username': message.chat.username,
                                  'first_name': message.chat.first_name, 'last_name': message.chat.last_name,
                                  'current_group': start_param[1]})
                # если пользователь есть в БД, обновляем его информацию
                # на случай ее изменения или перехода пользователя по другой ссылке
                else:
                    curs.execute('UPDATE Users SET username=:username, first_name=:first_name, last_name=:last_name, current_group=:current_group '
                                 'WHERE tg_id=:tg_id', {'username': message.chat.username,
                                  'first_name': message.chat.first_name, 'last_name': message.chat.last_name,
                                  'current_group': start_param[1], 'tg_id': message.chat.id})

                # узнаем id пользователя в БД
                curs.execute('SELECT id FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
                user_id = curs.fetchall()
                print(f'user_id = {user_id[0][0]}')
                print(f'group_id = {group_exists[0][0]}')

                # устанавливаем связь пользователя и группы, если её ещё нет в БД (пользователь перешел по ссылке впервые)
                curs.execute('SELECT * FROM Relations_user_group WHERE user_id=:user_id AND group_id=:group_id',
                             {'user_id': user_id[0][0], 'group_id': group_exists[0][0]})
                relation_exists = curs.fetchall()
                print(f'есть связь: {relation_exists}')
                if len(relation_exists) == 0:
                    curs.execute('INSERT INTO Relations_user_group(user_id, group_id) '
                                 'VALUES (:user_id, :group_id)',
                                 {'user_id': user_id[0][0], 'group_id': group_exists[0][0]})

                # узнаем название группы, в которую пришел пользователь
                curs.execute('SELECT title FROM Groups WHERE id=:id', {'id': group_exists[0][0]})
                group_title = curs.fetchall()

                conn.commit()
                conn.close()
                

                bot.send_message(message.chat.id, text=f'Привет! Я Санта-бот и ты пришел ко мне по приглашению '
                                                       f'в группу "{group_title[0][0]}"! '
                                                       'Для твоего подарка уже есть место под ёлкой!')

                # клавиатура
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_part')
                key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_part')
                keyboard.add(key_yes, key_no)
                question = 'Готов принять участие в розыгрыше?'
                bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            elif len(group_exists) == 1 and group_exists[0][3] == 1:
                bot.send_message(message.chat.id, text='Розыгрыш в этой группе уже завершен.'
                                                       'Ты можешь создать новую группу командой /newgroup.')
            else:
                bot.send_message(message.chat.id, text='Ссылка запуска недействительна.')


    else:
        bot.send_message(message.chat.id, 'Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes_group':
        # скрываем клаву после выбора
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        get_group_name(call.message) # вызываем функцию получения названия группы
        # код сохранения данных, или их обработки
    elif call.data == 'no_group':
        bot.send_message(call.message.chat.id, text='Ну ок. /newgroup если передумаешь или присоединяйся '
                                                    'к своей группе по ссылке от ведущего')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    elif call.data == 'yes_part':
        # меняем статус участия на 1
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()

        print('---------------')
        # вспоминаем id пользователя в БД
        curs.execute('SELECT id, current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': call.message.chat.id})
        current_user = curs.fetchall()
        print(current_user)
        print(f'user_id = {current_user[0][0]}')
        print(f'group_link = {current_user[0][1]}')
        # вспоминаем id группы, в которую пришёл пользователь
        curs.execute('SELECT id FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id = curs.fetchall()
        print(group_id[0][0])
        print('-----------------')

        # меняем статус участия на 1 в таблице связей
        curs.execute('UPDATE Relations_user_group SET participation=:participation '
                     'WHERE user_id=:user_id AND group_id=:group_id', {'participation': 1,
                                                                       'user_id': current_user[0][0], 'group_id': group_id[0][0]})
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, text='Введи пожелание к подарку или просто послание для своего Санты! 🎁 '
                                                    'Если хочешь сюрприз - сообщи об этом! '
                                                    '(Пока ты не можешь отказаться от этого шага.)')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        enter_wish(call.message) # вызываем функцию получения пожелания от игрока

    elif call.data == 'no_part':
        bot.send_message(call.message.chat.id, text='Если передумаешь, набери команду /participate.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    logcall(call)


def enter_wish(message): # получаем пожелание к подарку
    # bot.send_message(message.chat.id, text='Жду пожелания.')
    bot.register_next_step_handler(message, get_wish)
    logmess(message)


def get_wish(message):
    print(f'пожелание игрока: {message.text}')

    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
        if message.text[0] != '/':
            # работа с БД
            conn = sqlite3.connect("santa.db")
            curs = conn.cursor()
            # вспоминаем id пользователя в БД
            curs.execute('SELECT id, current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
            current_user = curs.fetchall()
            # вспоминаем id группы, в которую пришёл пользователь
            curs.execute('SELECT id FROM Groups WHERE link=:link', {'link': current_user[0][1]})
            group_id = curs.fetchall()
            # заносим/меняем пожелание в таблице связей
            curs.execute('UPDATE Relations_user_group SET wish=:wish '
                         'WHERE user_id=:user_id AND group_id=:group_id',
                         {'wish': message.text, 'user_id': current_user[0][0], 'group_id': group_id[0][0]})
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, text='Класс! Санта учтёт твоё пожелание (или нет). \n'
                                                   'Теперь жди розыгрыш! (подумать над датой)'
                                                   '(В теории ты сможешь изменять пожелание до дня розыгрыша командой /enterwish)')
        else:
            bot.send_message(message.chat.id,
                             text='Это не похоже на пожелание. (В теории ты сможешь изменять пожелание до дня розыгрыша командой /enterwish)')
    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)


def get_group_name(message): # получаем название группы
    bot.send_message(message.chat.id, text='Напиши название группы и я пришлю тебе ссылку-приглашение. '
                                           'Название не должно начинаться со слеша.')
    bot.register_next_step_handler(message, check_group_name) # вызываем проверку названия
    logmess(message)

# проверяем валидность названия
def check_group_name(message):

    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
        print(message.content_type)
        print(message.text[0])
        print(f'название: {message.text}')
        # проверяем, что введено название, а не команда (и оно уникально)
        if message.text[0] == '/':
            bot.send_message(message.chat.id, text='Ой! Команда? Это не подходит для названия группы. '
                                                   'Перейди по /newgroup, чтобы создать новую группу в будущем. '
                                                   'Название должно быть уникально в рамках твоих активных групп.')
        else:
            # если создающего пользователя нет в БД, то проверку на уникальность делать не надо
            conn = sqlite3.connect("santa.db")
            curs = conn.cursor()
            curs.execute('SELECT id FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
            user_id = curs.fetchall()
            print(user_id)
            # если пользователь есть в БД
            if len(user_id) != 0:
                curs.execute('SELECT * FROM Groups WHERE leader_id=:leader_id and title=:title and raffle=:raffle',
                             {'leader_id': user_id[0][0], 'title': message.text, 'raffle': 0})
                group_exists = curs.fetchall()
                # закрываем соединение
                conn.commit()
                conn.close()
                # проверяем уникальность названия (разный регистр - разное название)
                if len(group_exists) != 0:
                    bot.send_message(message.chat.id, text='Проказник! Это не подходит для названия группы. '
                                                           'Оно должно быть уникально в рамках твоих активных групп. '
                                                           'Перейди по /newgroup, чтобы попробовать ещё раз.')
                else:
                    link_generation(message)  # вызываем генерацию
            # если пользователя нет в БД
            else:
                # закрываем соединение
                conn.commit()
                conn.close()
                link_generation(message)  # вызываем генерацию
    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)


# генерация ссылки и занесение данных в БД
def link_generation(message):
    print(f'message.text: {message.text}')

    # генерация ссылки
    link_part = secrets.token_urlsafe(12)
    print(f'сгенерированная часть ссылки: {link_part}')
    link_full = 'https://t.me/shanta_bot?start=' + link_part
    print(f'полная ссылка: {link_full}')

    # сохранение в БД
    conn = sqlite3.connect("santa.db")
    curs = conn.cursor()
    curs.execute('SELECT * FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
    user_exists = curs.fetchall()
    # если ведущего нет в БД, заносим его туда
    if len(user_exists) == 0:
        curs.execute('INSERT INTO Users(tg_id, username, first_name, last_name, current_group) '
                     'VALUES (:tg_id, :username, :first_name, :last_name, :current_group)',
                     {'tg_id': message.chat.id, 'username': message.chat.username,
                      'first_name': message.chat.first_name, 'last_name': message.chat.last_name,
                      'current_group': link_part})
    # если ведущий есть в БД, обновляем его информацию на случай ее изменения
    # или прихода по другой ссылке
    else:
        curs.execute('UPDATE Users SET username=:username, first_name=:first_name, '
                     'last_name=:last_name, current_group=:current_group '
                     'WHERE tg_id=:tg_id', {'username': message.chat.username,
                                            'first_name': message.chat.first_name, 'last_name': message.chat.last_name,
                                            'current_group': link_part, 'tg_id': message.chat.id})
    # узнаем id ведущего, присвоенный в БД (автоинкремент)
    curs.execute('SELECT id FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
    user_id = curs.fetchall()
    # заносим новую группу в таблицу Group
    curs.execute('INSERT INTO Groups(title, link, raffle, leader_id) '
                 'VALUES (:title, :link, :raffle, :leader_id)',
                 {'title': message.text, 'link': link_part,
                  'raffle': 0, 'leader_id': user_id[0][0]})
    # узнаем id группы, присвоенный в БД (автоинкремент)
    curs.execute('SELECT id FROM Groups WHERE link=:link', {'link': link_part})
    group_new = curs.fetchall()
    print(f'id новой группы: {group_new[0][0]}')
    # устанавливаем связь ведущего и группы, если её ещё нет в БД (не повторный приход по ссылке)
    curs.execute('SELECT * FROM Relations_user_group WHERE user_id=:user_id AND group_id=:group_id',
                 {'user_id': user_id[0][0], 'group_id': group_new[0][0]})
    relation_exists = curs.fetchall()
    if len(relation_exists) == 0:
        # сразу устанавливаем статус участия в 1
        curs.execute('INSERT INTO Relations_user_group(user_id, group_id, participation) '
                     'VALUES (:user_id, :group_id, :participation)',
                     {'user_id': user_id[0][0], 'group_id': group_new[0][0], 'participation': 1})

    bot.send_message(message.chat.id, text=f'🎄 Годится-ягодица! Группа "{message.text}" создана!\n\n'
                                           f'🎄 Вот ссылка-приглашение на участие для твоих друзей: '
                                           f'{link_full}.\n\n'
                                           f'🎄 Чтобы ввести своё пожелание к подарку используй /enterwish.\n'
                                           f'🎄 Для отмены участия в розыгрыше: /leavegame.\n\n'
                                           f'🎄 После регистрации всех желающих ты можешь запустить розыгрыш '
                                           f'командой /rungame.\n\n')
    conn.commit()
    conn.close()
    logmess(message)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, text='/start - запустить бота 🎄\n'
                                               '/help - получить помощь 🎄\n'
                                               '/rungame - запустить розыгрыш (для ведущего) 🎄 (*)')
    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.message_handler(commands=['rungame'])
def send_welcome(message):
    if message.chat.type == 'private':
        # выбираем из бд активные группы текущего пользователя
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()
        curs.execute('SELECT id FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
        leader_id = curs.fetchall()
        curs.execute('SELECT title FROM Groups WHERE leader_id=:leader_id AND raffle=:raffle', {'leader_id': leader_id[0][0], 'raffle': 0})
        list_active_groups = curs.fetchall()
        print(list_active_groups)
        if len(list_active_groups) == 0:
            bot.send_message(message.chat.id, text='Оу, кажется, у тебя нет активных групп для розыгрыша! '
                                                   'Эта команда доступна только для ведущего.')
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            # заносим названия активных групп в кнопки
            for group in list_active_groups:
                title = group[0]
                button = types.KeyboardButton(text=title)
                keyboard.add(button)

            bot.send_message(message.chat.id,
                             "Выбери группу, в которой хочешь запустить розыгрыш! (Действие окончательно и необратимо.)",
                             reply_markup=keyboard)

            bot.register_next_step_handler(message, run_game)

        conn.commit()
        conn.close()

    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


def run_game(message):
    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
        bot.send_message(message.chat.id, text=f'Для розыгрыша выбрана группа "{message.text}"!',
                         reply_markup=ReplyKeyboardRemove())
        # логика розыгрыша!
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()

        # узнаём id выбранной группы
        curs.execute('SELECT id FROM Groups WHERE title=:title', {'title': message.text})
        group_id = curs.fetchall()

        if len(group_id) == 0:
            bot.send_message(message.chat.id, text='Упс. Такой группы то нет.')
        else:
            # выбираем id всех участников этой группы, сохраняем в список - ПАДАЕТ, ЕСЛИ ГРУПП НЕТ
            curs.execute(
                'SELECT user_id FROM Relations_user_group WHERE group_id=:group_id AND participation=:participation',
                {'group_id': group_id[0][0], 'participation': 1})
            all_participants = curs.fetchall()
            print('+++++++++++++++')
            print(all_participants)
            # формируем список из id участников
            list_user_id = []
            for i in range(len(all_participants)):
                list_user_id.append(all_participants[i][0])

            print(f'list: {list_user_id}')
            # перемешиваем участников
            shuffle(list_user_id)
            print(f'shuf_list: {list_user_id}')

            # логируем групу участников розыгрыша в файл
            # (или делать это после розыгрыша?)
            gr = group_id[0][0]
            now = datetime.now()

            # складываем файлы логов розыгрыша в папку
            with open(os.path.join(os.path.dirname(__file__), 'logs', f'logs_{gr}.txt'), 'w') as log_list:
                log_list.write(f'group_id: {str(gr)}\n')
                log_list.write(f'run_game: {now}\n')
                log_list.write('list_game: ')
                for i in list_user_id:
                    log_list.write(f'{str(i)}, ')

            # создаем словарь Сант: ключ-игрок, значение-Санта
            dict_sant = {}
            for i in range(len(list_user_id)):
                if i < len(list_user_id) - 1:
                    dict_sant.update({list_user_id[i]: list_user_id[i + 1]})
                else:
                    dict_sant.update({list_user_id[i]: list_user_id[0]})
            print(dict_sant)

            # выбираем всю инфу игрока по ключу и отправляем ее в чат Санте по значению
            # инфа: Users.first_name, Users.last_name, Relations_user_group.wish

            for key in dict_sant:
                curs.execute('SELECT us.first_name, us.last_name, us.username, rel.wish FROM Users as us '
                             'LEFT JOIN Relations_user_group as rel '
                             'ON us.id = rel.user_id '
                             'WHERE user_id=:user_id AND group_id=:group_id',
                             {'user_id': key, 'group_id': group_id[0][0]})
                info = curs.fetchall()
                santa_id = dict_sant[key]
                print(f'для санты: id={santa_id} --- игрок: {info}')
                print(f'santa_id: {santa_id}')

                # узнаем tg_id Санты по значению ключа
                curs.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': santa_id})
                santa_tg_id = curs.fetchall()
                print(f'santa_tg_id: {santa_tg_id[0][0]}')

                # ОБРАБОТАТЬ NONE - ВСЕ В ПЕРЕМЕННЫЕ ИМЯФАМ И ПОСЛАНИЯ
                # отправляем информацию Санте!
                bot.send_message(santa_tg_id[0][0], text=f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️☃️️\n\n'
                                                         f'Привет, солнышко. Вот и розыгрыш в группe "{message.text}"! 🎉\n'
                                                         f'Ты будешь Тайным Сантой для человека по имени '
                                                         f'{info[0][0]} {info[0][1]}! \n'
                                                         f'Его ник в телеграме: @{info[0][2]}.\n'
                                                         f'Его послание для тебя: {info[0][3]}.\n\n'
                                                         f'Ты можешь прислушаться к пожеланию по желанию 🎁\n\n'
                                                         f'Мира, любви, счастья, ура, чао-какао, я всё, до новых встреч!\n'
                                                         f'(Тексты мы, конечно, поправим...)\n\n'
                                                         f'🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄')

                # меняем статус розыгрыша raffle на 1 !
                curs.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
                             {'raffle': 1, 'id': group_id[0][0]})

        conn.commit()
        conn.close()

    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)


# обработка разных типов сообщений
@bot.message_handler(content_types=['text'])
def santa_text(message):
    bot.send_message(message.chat.id, text='Человек отправил мне текст. Ок.')
    logmess(message)

@bot.message_handler(content_types=['sticker'])
def santa_sticker(message):
    bot.send_message(message.chat.id, text='Человек меня стикерит. Ок.')
    logmess(message)

@bot.message_handler(content_types=['photo'])
def santa_photo(message):
    bot.send_message(message.chat.id, text='Человек отправил мне фото. Ок.')
    logmess(message)

@bot.message_handler(content_types=['document'])
def santa_document(message):
    bot.send_message(message.chat.id, text='Человек меня документит. Ок.')
    logmess(message)

@bot.message_handler(content_types=['voice'])
def santa_voice(message):
    bot.send_message(message.chat.id, text='Человек говорит со мной. Ок.')
    logmess(message)

@bot.message_handler(content_types=['audio'])
def santa_audio(message):
    bot.send_message(message.chat.id, text='Человек отправил мне аудио. Ок.')
    logmess(message)

@bot.message_handler(content_types=['video', 'video_note'])
def santa_video(message):
    bot.send_message(message.chat.id, text='Человек отправил мне видео. Ок.')
    logmess(message)

@bot.message_handler(content_types=['location'])
def santa_location(message):
    bot.send_message(message.chat.id, text='Человек отправил мне локацию. Ок.')
    logmess(message)

@bot.message_handler(content_types=['contact'])
def santa_contact(message):
    bot.send_message(message.chat.id, text='Человек отправил мне контакт. Ок.')
    logmess(message)



# # бот дразнится
# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     # bot.reply_to(message, message.text)  # ответ на сообщение
#     bot.send_message(message.chat.id, message.text)  # повторение сообщения

# # бот ругается
# @bot.message_handler(func=lambda message: True)
# def any_message(message):
#     bot.reply_to(message, "Сам {!s}".format(message.text))
#
# # бот редактирует свое ругательство после редактирования сообщения
# @bot.edited_message_handler(func=lambda message: True)
# def edit_message(message):
#     bot.edit_message_text(chat_id=message.chat.id,
#                           text= "Сам {!s}".format(message.text),
#                           message_id=message.message_id + 1)


def logmess(message):
    print(f'\nmessage: {message}') # можно убрать этот вывод
    print('\n***')
    print(datetime.now())
    print(f'{message.chat.first_name} {message.chat.last_name} '
          f'({message.chat.username} id={message.chat.id}) пишет:\n{message.text}\n')

def logcall(call):
    print(f'\ncall: {call}')


print('точно работает...')
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=20) # какое время ожидания ставить, чтобы бот не выключался без сообщений

print('сервер выключен...')