# -*- coding: utf-8 -*-

# import config
import importlib
import os
from urllib import response

import telebot
import sqlite3
import secrets
import datetime
import requests
import re
import request
import urllib.request
from idlelib import query
from random import shuffle
from datetime import datetime
from telebot import (apihelper, types)
# from config import (token, socks5)
from telebot.types import ReplyKeyboardRemove
from settings import *


if socks5 != None and socks5 != '':
    apihelper.proxy = {'https': socks5}

bot = telebot.TeleBot(token, threaded=False) # однопоточный режим
print('сервер работает...')
user = bot.get_me()



@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        start_param = message.text.split()
        if len(start_param) == 1:
            print('нет параметра запуска')
            bot.send_message(message.chat.id, text='Привет! Я Санта-бот, помогу провести новогодний '
                                                   'розыгрыш подарков в вашей компании! 🎄')
            keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура шириной в 2 кнопи в ряду
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_group')
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_group')
            keyboard.add(key_yes, key_no)  # добавляем кнопки в клавиатуру в один ряд
            # keyboard.add(key_no) # добавлять по одной кнопке в ряд
            question = 'Хочешь создать новую группу для розыгрыша? 🎄'
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
            # создаем связь с группой, если группа существует (иначе ссылка недействительна)
            curs.execute('SELECT * FROM Groups WHERE link=:link', {'link': start_param[1]})
            group_exists = curs.fetchall()
            print(f'есть группа: {group_exists}')

            # print(f'статус розыгрыша: raffle = {group_exists[0][3]}') # код падает, т.к группы еще может не быть
            print(f'количество групп: {len(group_exists)}')

            # проверяем, что raffle (group_exists[0][3]) равно 0 (розыгрыша не было)
            if len(group_exists) == 1 and group_exists[0][3] == 0:
                # если пользователя нет в БД, заносим его туда
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

                # узнаем название группы, в которую пришёл пользователь
                curs.execute('SELECT title FROM Groups WHERE id=:id', {'id': group_exists[0][0]})
                group_title = curs.fetchall()

                if len(relation_exists) == 0:
                    curs.execute('INSERT INTO Relations_user_group(user_id, group_id) '
                                 'VALUES (:user_id, :group_id)',
                                 {'user_id': user_id[0][0], 'group_id': group_exists[0][0]})

                    # первое привествие игрока! (однократное)
                    bot.send_message(message.chat.id, text=f'Привет! Я Санта-бот и ты пришёл ко мне по приглашению '
                                                           f'в группу «{group_title[0][0]}»! '
                                                           'Для твоего подарка уже есть место под ёлкой! 🎄')
                    # клавиатура
                    keyboard = types.InlineKeyboardMarkup(row_width=2)
                    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_part')
                    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_part')
                    keyboard.add(key_yes, key_no)
                    question = 'Готов принять участие в розыгрыше?'
                    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

                # связь с группой уже есть, значит это не первый переход по ссылке
                else:
                    bot.send_message(message.chat.id, text=f'С возвращением в группу «{group_title[0][0]}»! 🎄')
                    # тут проверим, пользователь участник или нет
                    # (да - сообщить - ты уже являешься её участником, нет - предложить им стать)
                    # relation_exists - выборка связи, relation_exists[0][2] - флаг участия (partisipation)

                    print('связь')
                    print(relation_exists)
                    print(relation_exists[0][2])
                    if relation_exists[0][2] == 1:
                        # хочешь ли продолжить игру? да - ок, нет - отменить участие
                        # снова та же клавиатура
                        keyboard = types.InlineKeyboardMarkup(row_width=2)
                        key_yes = types.InlineKeyboardButton(text='Конечно! 🎄', callback_data='yes_part_continue')
                        key_no = types.InlineKeyboardButton(text='Выйти', callback_data='no_part_continue')
                        keyboard.add(key_yes, key_no)
                        question = "Ты уже участвуешь в розыгрыше!\nГотов продолжить? 🎄"
                        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
                    else:
                        # снова та же клавиатура
                        keyboard = types.InlineKeyboardMarkup(row_width=2)
                        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_part')
                        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_part')
                        keyboard.add(key_yes, key_no)
                        question = "Ты ещё не подтвердил участие в розыгрыше.\nГотов играть? 🎄"
                        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

            elif len(group_exists) == 1 and group_exists[0][3] == 1:
                bot.send_message(message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                       'Для создания новой перезапусти бота командой /start.')
            else:
                bot.send_message(message.chat.id, text='Ссылка запуска недействительна.')

            conn.commit()
            conn.close()
    else:
        bot.send_message(message.chat.id, 'Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


# Обраотчик всех кнопок инлайновых клавиатур (где бы его расположить...)
@bot.callback_query_handler(func=lambda call: True)
def callback_group_part(call):

    data_parts = call.data.split(':')
    print(f'data_pars: {data_parts}')
    # data_parts[1] - id группы для розыгрыша

    # КНОПКИ СОЗДАНИЯ НОВОЙ ГРУППЫ
    # if call.data == 'yes_group':
    if data_parts[0] == 'yes_group':
        # скрываем клаву после выбора
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        get_group_name(call.message) # вызываем функцию получения названия группы
        # код сохранения данных, или их обработки
    elif data_parts[0] == 'no_group':
        bot.send_message(call.message.chat.id, text='Ладушки-оладушки. Eсли передумаешь, перезапусти бота командой /start '
                                                    'или присоединяйся к группе по ссылке от ведущего!')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # КНОПКИ СОГЛАСИЯ НА УЧАСТИЕ
    elif data_parts[0] == 'yes_part':
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
        # вспоминаем id группы, в которую пришёл пользователь и другую инфу
        curs.execute('SELECT id, raffle, description FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf_des = curs.fetchall()
        print(group_id_raf_des[0][0])
        print('-----------------')

        # прежде чем менять статуc, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf_des[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        # меняем статус участия на 1 в таблице связей
        curs.execute('UPDATE Relations_user_group SET participation=:participation '
                     'WHERE user_id=:user_id AND group_id=:group_id', {'participation': 1,
                                                                       'user_id': current_user[0][0], 'group_id': group_id_raf_des[0][0]})
        conn.commit()
        conn.close()

        # показываем описание группы от ведущего group_id_raf_des[0][2] - ECЛИ ОНО ЕСТЬ
        if group_id_raf_des[0][2] != None and group_id_raf_des[0][2] != '':
            bot.send_message(call.message.chat.id, text=f'Ура, ты в игре! 🎄 \n\n'
                                                        f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️☃️\n\n'
                                                        f'{group_id_raf_des[0][2]}\n\n'
                                                        f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️☃️')
        else:
            bot.send_message(call.message.chat.id, text='Ура, ты в игре! 🎄')

        # сообщать в какую группу принят

        bot.send_message(call.message.chat.id, text='Введи пожелание к подарку или просто послание для своего Тайного Санты! '
                                                    'Если хочешь сюрприз — сообщи об этом! 🎁')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        enter_wish(call.message) # вызываем функцию получения пожелания от игрока

    elif data_parts[0] == 'no_part':
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
        curs.execute('SELECT id, raffle FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf = curs.fetchall()
        print(group_id_raf[0][0])
        print('-----------------')
        # прежде чем ответить, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        bot.send_message(call.message.chat.id, text='Ладушки-оладушки. Если передумаешь, перейди по ссылке-приглашению вновь '
                                                    'и сделай правильный выбор! ;)')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        conn.commit()
        conn.close()

    # КНОПКИ СМЕНЫ СТАТУСА УЧАСТИЯ (ПОВТОРНЫЙ ПЕРЕХОД ПО ССЫЛКЕ)
    elif data_parts[0] == 'yes_part_continue':
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
        curs.execute('SELECT id, raffle FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf = curs.fetchall()
        print(group_id_raf[0][0])
        print('-----------------')
        # прежде чем ответить, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        bot.send_message(call.message.chat.id, text='Чудесно! Ждём подарки! 🎁')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        conn.commit()
        conn.close()

    elif data_parts[0] == 'no_part_continue':
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
        curs.execute('SELECT id, raffle FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf = curs.fetchall()
        print(group_id_raf[0][0])
        print('-----------------')
        # прежде чем ответить, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        # сообщать, в какой группе отменено участие

        bot.send_message(call.message.chat.id, text='Ну вот... Санта всхлипнул... \n'
                                                    'Твоё участие успешно отменено.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        # меняем статус участия на 0 в таблице связей
        curs.execute('UPDATE Relations_user_group SET participation=:participation '
                     'WHERE user_id=:user_id AND group_id=:group_id', {'participation': 0,
                                                                       'user_id': current_user[0][0],
                                                                       'group_id': group_id_raf[0][0]})
        conn.commit()
        conn.close()

    # КНОПКИ ПОДТВЕЖДЕНИЯ РОЗЫГРЫША
    elif data_parts[0] == 'yes_confirm':
        # скрываем клаву после выбора
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        # вызываем функцию запуска игры, передаём в неё id группы
        run_game(data_parts[1])

    elif data_parts[0] == 'no_confirm':
        bot.send_message(call.message.chat.id, text='Розыгрыш отменён.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # КНОПКИ ВВОДА ОПИСАНИЯ ГРУППЫ ОТ ВЕДУЩЕГО
    elif data_parts[0] == 'yes_description':
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()
        print('---------------')
        # вспоминаем id пользователя в БД
        curs.execute('SELECT id, current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': call.message.chat.id})
        current_user = curs.fetchall()
        print(current_user)
        print(f'user_id = {current_user[0][0]}')
        print(f'group_link = {current_user[0][1]}')
        # вспоминаем id группы, в которую пришёл пользователь и другую инфу
        curs.execute('SELECT id, raffle, description FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf_des = curs.fetchall()
        print(group_id_raf_des[0][0])
        print('-----------------')
        # прежде чем реагировать, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf_des[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        # выполняем, если розыгрыша не было
        conn.commit()
        conn.close()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        get_group_description(call.message)  # вызываем функцию получения описания группы

    elif data_parts[0] == 'no_description':
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()
        print('---------------')
        # вспоминаем id пользователя в БД
        curs.execute('SELECT id, current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': call.message.chat.id})
        current_user = curs.fetchall()
        print(current_user)
        print(f'user_id = {current_user[0][0]}')
        print(f'group_link = {current_user[0][1]}')
        # вспоминаем id группы, в которую пришёл пользователь и другую инфу
        curs.execute('SELECT id, raffle, description FROM Groups WHERE link=:link', {'link': current_user[0][1]})
        group_id_raf_des = curs.fetchall()
        print(group_id_raf_des[0][0])
        print('-----------------')
        # прежде чем менять статуc, нужно проверить, активна ли группа (на случай, если остались висящие кнопки, а розыгрыш уже был)
        if group_id_raf_des[0][1] == 1:
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, text='Розыгрыш в этой группе уже завершён. '
                                                        'Для создания новой перезапусти бота командой /start.')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            return

        # выполняем, если розыгрыша не было
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, text='Ладушки-оладушки. Ты можешь устно сообщить участникам ориентировочную стоимость подарка, '
                                                    'дату розыгрыша и дату торжественного вручения!')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


    logcall(call)


# что делает эта функция то? только передает управление дальше? зачем она тогда? :)
def enter_wish(message): # получаем пожелание к подарку
    # bot.send_message(message.chat.id, text='Жду пожелания.')
    bot.register_next_step_handler(message, get_wish)
    logmess(message)


def get_wish(message):
    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
        print(f'пожелание игрока: {message.text}')
        print(f'длина пожелания: {len(message.text)}')
        # ограничение длины пожелания
        if len(message.text) <= 1000:
            if message.text[0] != '/':
                # работа с БД
                conn = sqlite3.connect("santa.db")
                curs = conn.cursor()
                # вспоминаем id пользователя в БД
                curs.execute('SELECT id, current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
                current_user = curs.fetchall()
                # вспоминаем id группы, в которую пришёл пользователь
                # А ЕСЛИ НИ В КАКУЮ НЕ ПРИШЕЛ, ТО ПАДАЕТ (не пускать сюда из /enterwish без текущей группы
                curs.execute('SELECT id FROM Groups WHERE link=:link', {'link': current_user[0][1]})
                group_id = curs.fetchall()
                # заносим/меняем пожелание в таблице связей
                print('---------=========')
                print(current_user[0][0])
                print(group_id[0][0])
                curs.execute('UPDATE Relations_user_group SET wish=:wish '
                             'WHERE user_id=:user_id AND group_id=:group_id',
                             {'wish': message.text, 'user_id': current_user[0][0], 'group_id': group_id[0][0]})
                conn.commit()
                conn.close()
                # ути, моя прелесть (не уверена, что нужен стикер)
                # bot.send_sticker(message.chat.id, 'CAADAgADxQAD1JkmDfzbMn5BTH3LFgQ')
                bot.send_message(message.chat.id, text='Класс! 🎄 Тайный Санта учтёт твоё пожелание (или нет). \n'
                                                       'Теперь жди розыгрыша! 🎄\n'
                                                       'Кстати, ты можешь изменить пожелание командой /enterwish! 🎄')
            else:
                bot.send_message(message.chat.id, text='Это не похоже на пожелание. '
                                                       'Ты можешь попробовать снова с помощью команды /enterwish!')
        else:
            bot.send_message(message.chat.id, text='Пожелание слишком длинное. Похоже, ты слишком многого хочешь? :) '
                                                   'Ограничь описание своих аппетитов 1000 символами :) '
                                                   'Для ввода нового пожелания используй /enterwish 🎁!')
    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)


def get_group_name(message): # получаем название группы
    bot.send_message(message.chat.id, text='Напиши название группы, и я пришлю тебе ссылку-приглашение. '
                                           'Название не должно начинаться со слеша.')
    bot.register_next_step_handler(message, check_group_name) # вызываем проверку названия
    logmess(message)


def get_group_description(message): # получаем описание группы
    bot.send_message(message.chat.id, text='Советую написать ориентировочную стоимость подарка, '
                                           'дату розыгрыша и дату торжественного вручения! '
                                           'Длина текста не должна превышать 1000 символов '
                                           'и отредактировать отправленное описание будет нельзя ;)')
    bot.register_next_step_handler(message, check_group_description)  # вызываем проверку описания
    logmess(message)


# проверяем валидность названия
def check_group_name(message):

    # проверка типа (должен быть только текст)
    # запрещаем назвать группу "Отмена" - только в этом регистре
    if message.content_type == 'text' and message.text != 'Отмена':
        # название кнопки должно содержать не более 140 символов
        print(f'длина названия для кнопки: {len(message.text)}')
        if len(message.text) <= 140:
            print(message.content_type)
            print(message.text[0])
            print(f'название: {message.text}')
            # проверяем, что введено название, а не команда (и оно уникально)
            if message.text[0] == '/':
                bot.send_message(message.chat.id, text='Ой! Команда? Это не подходит для названия группы. '
                                                       'Перезапусти бота командой /start, чтобы создать новую группу '
                                                       'в будущем. '
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
                                                               'Перезапусти бота командой /start, чтобы попробовать ещё раз.')
                    else:

                        link_generation(message)  # вызываем генерацию
                # если пользователя нет в БД
                else:
                    # закрываем соединение
                    conn.commit()
                    conn.close()
                    link_generation(message)  # вызываем генерацию

        else:
            bot.send_message(message.chat.id, text='Упс. Название группы слишком длинное! '
                                                   'Оно должно содержать не более 200 символов')
    elif message.content_type == 'text' and message.text == 'Отмена':
        bot.send_message(message.chat.id, text='Проказник! Это не подходит для названия группы. '
                                               'Перезапусти бота командой /start, чтобы попробовать ещё раз.')
    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)


def check_group_description(message):
    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
        # ограничим описание 1000 символами
        if len(message.text) <= 1000:
            print(f'описание: {message.text}')
            # проверяем, что введено название, а не команда
            if message.text[0] == '/':
                bot.send_message(message.chat.id, text='Ой! Команда? Это не подходит для описания группы. '
                                                       'Теперь ты можешь устно сообщить участникам ориентировочную стоимость подарка, '
                                                       'дату розыгрыша и дату торжественного вручения! 🎁')
            else:
                # по tg_id - message.chat.id находим текущую сессию - current_group
                # по сессии находим группу в Groups, чтобы добавить туда описание

                conn = sqlite3.connect("santa.db")
                curs = conn.cursor()
                # # вспоминаем текущую группу ведущего
                curs.execute('SELECT current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
                curr_group = curs.fetchall()
                curs.execute('UPDATE Groups SET description=:description WHERE link=:link', {'description': message.text, 'link': curr_group[0][0]})
                conn.commit()
                conn.close()

                print(message)
                bot.send_message(message.chat.id, text='Чудно! Информация успешно сохранена 🎄')

        else:
            bot.send_message(message.chat.id, text='Упс. Описание группы слишком длинное! '
                                                   'Оно должно содержать не более 1000 символов. '
                                                   'Теперь ты можешь устно сообщить участникам ориентировочную стоимость подарка, '
                                                   'дату розыгрыша и дату торжественного вручения! 🎁')
    else:
        bot.send_message(message.chat.id, text='Санта не согласен!')

    logmess(message)



# генерация ссылки и занесение данных в БД
def link_generation(message):
    print(f'message.text: {message.text}')
    print(f'link_generation - {message}')

    # генерация ссылки
    link_part = secrets.token_urlsafe(12)
    print(f'сгенерированная часть ссылки: {link_part}')
    # link_full = 'https://t.me/shanta_bot?start=' + link_part
    print(f'bot_username: {bot_username}')
    link_full = f"https://t.me/{bot_username}?start={link_part}"
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
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, text=f'🎄 Годится-ягодица! Группа «{message.text}» создана!\n\n'
                                           f'🎄 Вот ссылка-приглашение на участие для твоих друзей: '
                                           f'{link_full}.\n\n'
                                           f'🎄 Ты можешь ввести своё пожелание к подарку с помощью команды /enterwish.\n\n'
                                           f'🎄 После регистрации всех желающих запускай розыгрыш '
                                           f'командой /rungame.\n\n')

    # клавиатура
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_description')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_description')
    keyboard.add(key_yes, key_no)
    question = 'Хочешь ввести дополнительную информацию для друзей, которую они увидят после подтверждения участия в розыгрыше?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

    logmess(message)


@bot.message_handler(commands=['help'])
def give_help(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, text='/start — запустить бота и создать новую группу 🎄\n'
                                               '/help — получить помощь 🎄\n'
                                               '/enterwish — ввести новое пожелание к подарку 🎄\n'
                                               '/rungame — запустить розыгрыш (для ведущего) 🎄')
    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.message_handler(commands=['smarthead'])
def smart_head(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, text='Я люблю SmartHead! ❤️❤️❤️')
    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.message_handler(commands=['enterwish'])
def enter_new_wish(message):
    if message.chat.type == 'private':
        # проверяем, что пользователь есть в бд и у него есть текущая группа
        # Если есть парамтр запуска, то не давать выбирать, если нет - это обработано уже

        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()
        curs.execute('SELECT current_group FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
        user_curr_gr = curs.fetchall()
        conn.commit()
        conn.close()

        if user_curr_gr[0][0] != None:

            bot.send_message(message.chat.id, text='Санта ждёт твоего пожелания! 🎁')
            bot.register_next_step_handler(message, get_wish)

        else:
            bot.send_message(message.chat.id, text='Начни с команды /start и создай свою первую группу для розыгрыша подарков! '
                                                   'Или присоединяйся к группе по ссылке от ведущего! 🎄')


    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.message_handler(commands=['rungame'])
def start_game(message):
    if message.chat.type == 'private':
        # выбираем из бд активные группы текущего пользователя, ЕСЛИ ОН ЕСТЬ В БД!
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()
        curs.execute('SELECT id FROM Users WHERE tg_id=:tg_id', {'tg_id': message.chat.id})
        leader_id = curs.fetchall()

        if len(leader_id) != 0:

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

                button_cancel = types.KeyboardButton(text='Отмена')
                keyboard.add(button_cancel)

                bot.send_message(message.chat.id,
                                 "Выбери группу, в которой хочешь запустить розыгрыш! "
                                 "(Действие окончательно и необратимо.)",
                                 reply_markup=keyboard)

                bot.register_next_step_handler(message, confirm_run_game)

        else:
            bot.send_message(message.chat.id, text='Привет, я Санта-бот! 🎄 \n'
                                                   'Начни с команды /start и создай свою первую группу для розыгрыша подарков! 🎄 '
                                                   'Или присоединяйся к группе по ссылке от ведущего! 🎄')

        conn.commit()
        conn.close()

    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


def confirm_run_game(message):

    # обработка Отмены (убить клавиатуру)
    if message.content_type == 'text' and message.text == 'Отмена':
        bot.send_message(message.chat.id, text='Розыгрыш отменён.', reply_markup=ReplyKeyboardRemove())
        return

    if message.content_type == 'text' and message.text[0] != '/':
        # сразу избавляемся от клавиатуры
        # bot.send_message(message.chat.id, text='Скрыть клавиатуру без текста нельзя',
        #                  reply_markup=ReplyKeyboardRemove())

        # логика розыгрыша
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()

        # узнаём tg_id ведущего для логов и для отправки
        # message.chat.id ? ведь только ведущий может "дойти" до этого кода?
        print(f'ВЕДУЩИЙ - {message.chat.id}')

        # узнаём id выбранной группы (можно взять и БД-шный id для логов)
        # будем его передвать в обработчик кнопок и в функцию запуска
        # НУЖНО ПРОВЕРИТЬ, ЧТО ВРУЧНУЮ НЕ ВВЕДЕНА ГРУППА, В КОТОРОЙ УЖЕ БЫЛ РОЗЫГРЫШ
        curs.execute('SELECT id FROM Groups WHERE title=:title '
                     'AND raffle=:raffle', {'title': message.text, 'raffle': 0})
        group_id = curs.fetchall()

        if len(group_id) == 0:
            # убить клавиатуру
            bot.send_message(message.chat.id, text='Упс. Среди активных групп такой группы нет. '
                                                   'Убедись в правильности названия и выбери '
                                                   'из предлагаемых вариантов.', reply_markup=ReplyKeyboardRemove())
        else:
            # cкрываем клавиатуру здесь (это не поздно?)
            # ЗАПРАШИВАТЬ ПОДТВЕРЖДЕНИЕ ЗАПУСКА В ВЕРНО ВЫБРАННОЙ ГРУППЕ
            bot.send_message(message.chat.id, text=f'Для розыгрыша выбрана группа «{message.text}»! 🎄',
                             reply_markup=ReplyKeyboardRemove())

            # клавиатура
            keyboard_confirm = types.InlineKeyboardMarkup(row_width=2)
            key_confirm_yes = types.InlineKeyboardButton(text='Пуск! 🎄', callback_data=f'yes_confirm:{group_id[0][0]}')
            key_confirm_no = types.InlineKeyboardButton(text='Отмена', callback_data='no_confirm')
            keyboard_confirm.add(key_confirm_yes, key_confirm_no)
            question = 'Требуется подтверждение запуска: 3, 2, 1...'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard_confirm)

        conn.commit()
        conn.close()
    elif message.content_type == 'text' and message.text[0] == '/':
        bot.send_message(message.chat.id, text='Ой! Команда? Не похоже на название группы. '
                                               'Убедись в правильности названия и выбери '
                                               'из предлагаемых вариантов.',
                         reply_markup=ReplyKeyboardRemove())
    else:
        # убить клавиатуру
        bot.send_message(message.chat.id, text='Санта не согласен!', reply_markup=ReplyKeyboardRemove())

    logmess(message)


# ВЫОЛНЕНИЕ РОЗЫГРЫША ТОЛЬКО В ПОСЛЕ ПОДТВЕРЖДЕНИЯ
def run_game(run_group_id):

    # run_group_id - это пришедший из кнопки group_id
    print(f'данные из обработки кнопок: {run_group_id}\n')

    conn = sqlite3.connect("santa.db")
    curs = conn.cursor()

    # берём id группы, leader_id и title по одному известному id группы (id, чтобы оперировать понятными названиями)
    curs.execute('SELECT id, leader_id, title FROM Groups WHERE id=:id', {'id': run_group_id})
    group_data = curs.fetchall()

    # находим tg_id ведущего по его бд_id
    curs.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': group_data[0][1]})
    leader_telegram_id = curs.fetchall()

    # тут проверим, что в этой активной группе, есть участники
    curs.execute('SELECT * FROM Relations_user_group WHERE group_id=:group_id '
                 'AND participation=:participation',
                 {'group_id': run_group_id, 'participation': 1})
    participants = curs.fetchall()
    # если участников нет, то меняем статус розыгрыша на 1 и выходим
    if len(participants) == 0:

        bot.send_message(leader_telegram_id[0][0], text=f'В данной группе нет участников. Группа закрыта. '
                                                        f'Создать новую ты можешь командой /start!')

        # меняем статус розыгрыша на 1
        curs.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
                     {'raffle': 1, 'id': run_group_id})
        # СОХРАНЯЕМ ИЗМЕНЕНИЯ, РАЗРЫВАЕМ СОЕДИНЕНИЕ
        conn.commit()
        conn.close()
        # и убираемся отсюда
        return

    # выбираем id всех участников этой группы, сохраняем в список, ПАДАЕТ ЕСЛИ ГРУПП НЕТ
    curs.execute('SELECT user_id FROM Relations_user_group WHERE group_id=:group_id '
                 'AND participation=:participation',
                 {'group_id': group_data[0][0], 'participation': 1})
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
    gr = run_group_id
    now = datetime.now()

    # складываем файлы логов розыгрыша в папку
    with open(os.path.join(os.path.dirname(__file__), 'logs', f'logs_{gr}.txt'), 'w') as log_list:
        log_list.write(f'group_id: {str(gr)}\n')
        log_list.write(f'run_game: {now}\n')
        log_list.write(f'leader tg_id: {group_data[0][1]}\n')
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
                     {'user_id': key, 'group_id': group_data[0][0]})
        info = curs.fetchall()
        santa_id = dict_sant[key]
        print(f'для санты: id={santa_id} --- игрок: {info}')
        print(f'santa_id: {santa_id}')

        # узнаем tg_id Санты по значению ключа
        curs.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': santa_id})
        santa_tg_id = curs.fetchall()
        print(f'santa_tg_id: {santa_tg_id[0][0]}')

        # Обработка None в сообщении для Тайного Санты
        if info[0][0] == None or info[0][0] == '':
            player_name = info[0][1]
        elif info[0][1] == None or info[0][1] == '':
            player_name = info[0][0]
        else:
            player_name = f'{info[0][0]} {info[0][1]}'

        if info[0][2] == None or info[0][2] == '':
            player_username = 'отсутствует'
        else:
            player_username = f'@{info[0][2]}'

        if info[0][3] == None or info[0][3] == '':
            player_wish = 'не написано'
        else:
            player_wish = f'_«{info[0][3]}»_'

        # бот должен проверять доступность юзера перед отправкой, чтобы не падать
        print(f'santa_tg_id: {santa_tg_id[0][0]}')
        try:
            # отправляем информацию Санте!
            bot.send_message(santa_tg_id[0][0], parse_mode='Markdown',
                             text=f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️️☃️️\n\n'
                                  f'Ура! Розыгрыш в группe «{group_data[0][2]}» завершён! ✨\n\n'
                                  f'Ты будешь Тайным Сантой для человека по имени '
                                  f'{player_name}! \n'
                                  f'Его ник в телеграме: {player_username}.\n'
                                  f'Его послание для тебя: {player_wish} ✨\n\n'
                                  f'Ты можешь прислушаться к пожеланию, если хочешь.\n\n'
                                  f'Счастливого Нового Года и до новых встреч! ✨\n\n'
                                  f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️☃️')
        except telebot.apihelper.ApiException:
            print('ветка исключений......')

            # узнаем данные Пропавшего Тайного Санты по значению его tg_id
            curs.execute('SELECT first_name, last_name, username FROM Users WHERE tg_id=:tg_id',
                         {'tg_id': santa_tg_id[0][0]})
            missing_santa = curs.fetchall()
            print(f'missing_santa: {missing_santa}')

            if missing_santa[0][0] == None or missing_santa[0][0] == '':
                missing_santa_name = missing_santa[0][1]
            elif missing_santa[0][1] == None or missing_santa[0][1] == '':
                missing_santa_name = missing_santa[0][0]
            else:
                missing_santa_name = f'{missing_santa[0][0]} {missing_santa[0][1]}'

            print(f'missing_santa: {missing_santa}')
            print(f'leader_tg_id: {leader_telegram_id[0][0]}')

            if info[0][3] == None or info[0][3] == '':
                pl_wish = 'отсутствует'
            else:
                pl_wish = f'«_{info[0][3]}_»'
                print(f'pl_wish: {pl_wish}')

            if missing_santa[0][2] == None or missing_santa[0][2] == '':
                santa_username = 'отсутствует'
            else:
                santa_username = f'@{missing_santa[0][2]}'

            if info[0][2] == None or info[0][2] == '':
                play_username = 'отсутствует'
            else:
                play_username = f'@{info[0][2]}'

            # bot.send_message(leader_telegram_id[0][0], text=f'🔴 Бедствие: пропавший Тайный Санта! 🔴 \n\n'
            #                                                 f'Игрок {missing_santa_name} — {santa_username} '
            #                                                 f'не получил послaние игрока {player_name} — {play_username} '
            #                                                 f'{pl_wish} 🥺 \n\n'
            #                                                 f'Сообщи устно и проследи, чтобы {player_name} и подарок встретились! ✨',
            #                  parse_mode='Markdown')

            bot.send_message(leader_telegram_id[0][0], parse_mode='Markdown',
                             text=f'🔴 Бедствие: пропавший Тайный Санта! 🔴 \n\n'
                                  f'Игрок: {missing_santa_name}\n'
                                  f'телеграм-ник: {santa_username}\n'
                                  f'не получил послaние 🥺\n'
                                  f'игрока: {player_name}\n'
                                  f'телеграм-ник: {play_username}\n'
                                  f'пожелание: {pl_wish} \n\n'
                                  f'Сообщи устно и проследи, чтобы {player_name} и подарок встретились! ✨')

        # меняем статус розыгрыша raffle на 1
        curs.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
                     {'raffle': 1, 'id': group_data[0][0]})

    conn.commit()
    conn.close()

    # аудио для ведущего
    bot.send_audio(leader_telegram_id[0][0],
                   audio=open(os.path.join(os.path.dirname(__file__), 'music', 'Kaby_ne_bylo_zimy.mp3'), 'rb'),
                   caption='Игра успешно закончена. Санта гордится тобой! 🎄',
                   performer='Простоквашино',
                   title='Кабы...')
    bot.send_sticker(leader_telegram_id[0][0], 'CAADAgADuQAD1JkmDXikIH-iJs3EFgQ')


# обработка разных типов сообщений

# текст обрабатывается в ручном вводе названия группы
@bot.message_handler(content_types=['text'])
def santa_text(message):
    # необходимая пасхалка для Барского
    if message.text.lower() == 'хуй':
        bot.send_sticker(message.chat.id, 'CAADAgADwAAD1JkmDRREnT9mK6BvFgQ')
    # кажется, Игорь не согласен
    # elif message.text.lower() == 'пизда':
    #     bot.send_sticker(message.chat.id, 'CAADAgAD0wAD1JkmDRI4IyyS5lBtFgQ')
    else:
        bot.reply_to(message, f'Сам {message.text} 🎅🏽')
        # bot.send_message(message.chat.id, text='Санту не пересантишь текстами! 🎅🏽')
    logmess(message)

# бот редактирует свое ругательство после редактирования сообщения
@bot.edited_message_handler(func=lambda message: True)
def edit_message(message):
    bot.edit_message_text(chat_id=message.chat.id,
                          text= f'Сам {message.text} 🎅🏽',
                          message_id=message.message_id + 1)

@bot.message_handler(content_types=['sticker'])
def santa_sticker(message):
    bot.send_sticker(message.chat.id, 'CAADAgADswAD1JkmDeRY6OpJBI6iFgQ')
    bot.send_message(message.chat.id, text='Стикерит, стикерит, да не перестикерит! 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['photo'])
def santa_photo(message):
    bot.send_message(message.chat.id, text='Санта смотрит на фото 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['document'])
def santa_document(message):
    bot.send_message(message.chat.id, text='Человек Санту отдокументил... 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['voice'])
def santa_voice(message):
    bot.send_message(message.chat.id, text='Санта выслушал человека 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['audio'])
def santa_audio(message):
    bot.send_message(message.chat.id, text='Санта станцевал под твою музыку 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['video', 'video_note'])
def santa_video(message):
    bot.send_message(message.chat.id, text='Санта не смотрит телевизор! 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['location'])
def santa_location(message):
    bot.send_message(message.chat.id, text='Санта не пойдёт искать человека 🎅🏽')
    logmess(message)

@bot.message_handler(content_types=['contact'])
def santa_contact(message):
    bot.send_message(message.chat.id, text='Санта избегает контактов! 🎅🏽')
    logmess(message)


# логи в консоль
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