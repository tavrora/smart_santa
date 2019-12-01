# -*- coding: utf-8 -*-

# import config
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
                                                       f'в группу «{group_title[0][0]}»! '
                                                       'Для твоего подарка уже есть место под ёлкой!')

                # клавиатура
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_part')
                key_no = types.InlineKeyboardButton(text='Нет', callback_data='no_part')
                keyboard.add(key_yes, key_no)
                question = 'Готов принять участие в розыгрыше?'
                bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            elif len(group_exists) == 1 and group_exists[0][3] == 1:
                bot.send_message(message.chat.id, text='Розыгрыш в этой группе уже завершен. '
                                                       'Для создания новой перезапусти бота командой /start.')
            else:
                bot.send_message(message.chat.id, text='Ссылка запуска недействительна.')


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
        bot.send_message(call.message.chat.id, text='Ну ок. Eсли передумаешь, перезапусти бота командой /start '
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

    elif data_parts[0] == 'no_part':
        # А ЕСЛИ ОН УЖЕ В ГРУППУ (ПОВТОРНЫЙ ПЕРЕХОД ПО ССЫЛКЕ) - ЧТО ДОЛЖНО БЫТЬ ПРИ КЛИКЕ НА "НЕТ"?
        bot.send_message(call.message.chat.id, text='Если передумаешь, перейди по ссылке-приглашению вновь '
                                                    'и сделай правильный выбор! ;)')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    # КНОПКИ ПОДТВЕЖДЕНИЯ РОЗЫГРЫША
    elif data_parts[0] == 'yes_confirm':
        # скрываем клаву после выбора
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        # КАК ПЕРЕДАТЬ ID ГРУППЫ data_parts[1]
        # run_game(call.message) # вызываем функцию запуска игры
        run_game(data_parts[1]) # вызываем функцию запуска игры

        # код сохранения данных, или их обработки
    elif data_parts[0] == 'no_confirm':
        bot.send_message(call.message.chat.id, text='Розыгрыш отменён.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    logcall(call)


# что делает эта функция то? только передает управление дальше? зачем она тогда? :)
def enter_wish(message): # получаем пожелание к подарку
    # bot.send_message(message.chat.id, text='Жду пожелания.')
    bot.register_next_step_handler(message, get_wish)
    logmess(message)


def get_wish(message):
    print(f'пожелание игрока: {message.text}')
    print(f'длина пожелания: {len(message.text)}')

    # проверка типа (должен быть только текст)
    if message.content_type == 'text':
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
                                                       'Кстати, ты можешь изменить своё пожелание до проведения розыгрыша. '
                                                       'Для этого перейди по ссылке-приглашению вновь '
                                                       'и введи новое пожелание!')
            else:
                bot.send_message(message.chat.id, text='Это не похоже на пожелание. '
                                                       'Ты можешь изменить его до проведения розыгрыша. '
                                                       'Для этого перейди по ссылке-приглашению вновь '
                                                       'и введи новое пожелание!')
        else:
            bot.send_message(message.chat.id, text='Пожелание слишком длинное. Похоже, ты слишком многого хочешь? :) '
                                                   'Ограничь описание своих аппетитов 1000 символами :) '
                                                   'Для ввода нового пожелания перейди по ссылке-приглашению вновь!')
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

    bot.send_message(message.chat.id, text=f'🎄 Годится-ягодица! Группа «{message.text}» создана!\n\n'
                                           f'🎄 Вот ссылка-приглашение на участие для твоих друзей: '
                                           f'{link_full}.\n\n'
                                           f'🎄 Чтобы ввести своё пожелание к подарку перейди по ней.\n\n'
                                    
                                           f'🎄 После регистрации всех желающих ты можешь запустить розыгрыш '
                                           f'командой /rungame.\n\n')
    conn.commit()
    conn.close()
    logmess(message)


@bot.message_handler(commands=['help'])
def give_help(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, text='/start - запустить бота 🎄\n'
                                               '/help - получить помощь 🎄\n'
                                               '/rungame - запустить розыгрыш (для ведущего) 🎄 (*)')
    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.message_handler(commands=['rungame'])
def start_game(message):
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

            button_cancel = types.KeyboardButton(text='Отмена')
            keyboard.add(button_cancel)

            bot.send_message(message.chat.id,
                             "Выбери группу, в которой хочешь запустить розыгрыш! "
                             "(Действие окончательно и необратимо.)",
                             reply_markup=keyboard)

            bot.register_next_step_handler(message, confirm_run_game)

        conn.commit()
        conn.close()

    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


def confirm_run_game(message):

    # обработка Отмены (убить клавиатуру)
    if message.content_type == 'text' and message.text == 'Отмена':
        bot.send_message(message.chat.id, text='Окей, отмена.', reply_markup=ReplyKeyboardRemove())
        return

    # проверка типа (должен быть только текст)  and message.text != 'Отмена'
    if message.content_type == 'text':
        # сразу избавляемся от клавиатуры
        # bot.send_message(message.chat.id, text='Скрыть клавиатуру без текста нельзя',
        #                  reply_markup=ReplyKeyboardRemove())

        # логика розыгрыша!
        conn = sqlite3.connect("santa.db")
        curs = conn.cursor()

        # узнаём tg_id ведущего для логов и для отправки
        # message.chat.id ? ведь только ведущий может "дойти" до этого кода?
        print(f'ВЕДУЩИЙ - {message.chat.id}')

        # узнаём id выбранной группы (можно взять и БД-шный id для логов)
        # будем его передвать в обработчик кнопок и в функцию запуска
        curs.execute('SELECT id FROM Groups WHERE title=:title', {'title': message.text})
        group_id = curs.fetchall()

        if len(group_id) == 0:
            # убить клавиатуру
            bot.send_message(message.chat.id, text='Упс. Такой группы то нет.', reply_markup=ReplyKeyboardRemove())
        else:
            # cкрываем клваиатуру здесь (это не поздно?)
            # ЗАПРАШИВАТЬ ПОДТВЕРЖДЕНИЕ ЗАПУСКА В ВЕРНО ВЫБРАННОЙ ГРУППЕ
            bot.send_message(message.chat.id, text=f'Для розыгрыша выбрана группа «{message.text}»! ',
                             reply_markup=ReplyKeyboardRemove())
            # клавиатура
            keyboard_confirm = types.InlineKeyboardMarkup(row_width=2)
            key_confirm_yes = types.InlineKeyboardButton(text='Пуск!', callback_data=f'yes_confirm:{group_id[0][0]}')
            key_confirm_no = types.InlineKeyboardButton(text='Отмена', callback_data='no_confirm')
            keyboard_confirm.add(key_confirm_yes, key_confirm_no)
            question = 'Требуется подтверждение запуска: 3, 2, 1...'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard_confirm)

        #     # ВЫОЛНЕНИЕ ЛОГИКИ РОЗЫГРЫША ТОЛЬКО В ПОСЛЕ ПОДТВЕРЖДЕНИЯ
        #     # выбираем id всех участников этой группы, сохраняем в список, ПАДАЛО ЕСЛИ ГРУПП НЕТ
        #     curs.execute(
        #         'SELECT user_id FROM Relations_user_group WHERE group_id=:group_id AND participation=:participation',
        #         {'group_id': group_id[0][0], 'participation': 1})
        #     all_participants = curs.fetchall()
        #     print('+++++++++++++++')
        #     print(all_participants)
        #     # формируем список из id участников
        #     list_user_id = []
        #     for i in range(len(all_participants)):
        #         list_user_id.append(all_participants[i][0])
        #
        #     print(f'list: {list_user_id}')
        #     # перемешиваем участников
        #     shuffle(list_user_id)
        #     print(f'shuf_list: {list_user_id}')
        #
        #     # логируем групу участников розыгрыша в файл
        #     # (или делать это после розыгрыша?)
        #     gr = group_id[0][0]
        #     now = datetime.now()
        #
        #     # складываем файлы логов розыгрыша в папку
        #     with open(os.path.join(os.path.dirname(__file__), 'logs', f'logs_{gr}.txt'), 'w') as log_list:
        #         log_list.write(f'group_id: {str(gr)}\n')
        #         log_list.write(f'run_game: {now}\n')
        #         log_list.write(f'leader tg_id: {message.chat.id}\n')
        #         log_list.write('list_game: ')
        #         for i in list_user_id:
        #             log_list.write(f'{str(i)}, ')
        #
        #     # создаем словарь Сант: ключ-игрок, значение-Санта
        #     dict_sant = {}
        #     for i in range(len(list_user_id)):
        #         if i < len(list_user_id) - 1:
        #             dict_sant.update({list_user_id[i]: list_user_id[i + 1]})
        #         else:
        #             dict_sant.update({list_user_id[i]: list_user_id[0]})
        #     print(dict_sant)
        #
        #     # выбираем всю инфу игрока по ключу и отправляем ее в чат Санте по значению
        #     # инфа: Users.first_name, Users.last_name, Relations_user_group.wish
        #
        #     for key in dict_sant:
        #         curs.execute('SELECT us.first_name, us.last_name, us.username, rel.wish FROM Users as us '
        #                      'LEFT JOIN Relations_user_group as rel '
        #                      'ON us.id = rel.user_id '
        #                      'WHERE user_id=:user_id AND group_id=:group_id',
        #                      {'user_id': key, 'group_id': group_id[0][0]})
        #         info = curs.fetchall()
        #         santa_id = dict_sant[key]
        #         print(f'для санты: id={santa_id} --- игрок: {info}')
        #         print(f'santa_id: {santa_id}')
        #
        #         # узнаем tg_id Санты по значению ключа
        #         curs.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': santa_id})
        #         santa_tg_id = curs.fetchall()
        #         print(f'santa_tg_id: {santa_tg_id[0][0]}')
        #
        #         # Обработка None в сообщении для Тайного Санты
        #         player_name = ''
        #         player_wish = ''
        #
        #         if info[0][0] == None:
        #             player_name = info[0][1]
        #         elif info[0][1] == None:
        #             player_name = info[0][0]
        #         else:
        #             player_name = f'{info[0][0]} {info[0][1]}'
        #
        #         if info[0][3] != None:
        #             player_wish = info[0][3]
        #         else:
        #             player_wish = 'не написано'
        #
        #         # бот должен проверять доступность юзера перед отправкой, чтобы не падать
        #         try:
        #             # отправляем информацию Санте!
        #             bot.send_message(santa_tg_id[0][0], text=f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️️☃️️\n\n'
        #                                                      f'Привет! Вот и розыгрыш в группe «{message.text}»! 🎉\n'
        #                                                      f'Ты будешь Тайным Сантой для человека по имени '
        #                                                      f'{player_name}! \n'
        #                                                      f'Его ник в телеграме: @{info[0][2]}.\n'
        #                                                      f'Его послание для тебя: {player_wish}.\n\n'
        #                                                      f'Ты можешь прислушаться к пожеланию по желанию 🎁\n\n'
        #                                                      f'Мира, любви, счастья, ура, чао-какао, я всё, до новых встреч!\n'
        #                                                      f'(Тексты мы, конечно, поправим...)\n\n'
        #                                                      f'🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄')
        #         except telebot.apihelper.ApiException:
        #             print('ветка исключений......')
        #
        #             # узнаем данные Пропавшего Тайного Санты по значению его tg_id
        #             curs.execute('SELECT first_name, last_name, username FROM Users WHERE tg_id=:tg_id', {'tg_id': santa_tg_id[0][0]})
        #             missing_santa = curs.fetchall()
        #             print(f'missing_santa: {missing_santa}')
        #
        #             if missing_santa[0][0] == None:
        #                 missing_santa_name = missing_santa[0][1]
        #             elif missing_santa[0][1] == None:
        #                 missing_santa_name = missing_santa[0][0]
        #             else:
        #                 missing_santa_name = f'{missing_santa[0][0]} {missing_santa[0][1]}'
        #
        #             bot.send_message(message.chat.id, text=f'🔴 Бедствие: пропавший Тайный Санта! 🔴 \n\n'
        #                                                    f'Игрок {missing_santa_name} - @{missing_santa[0][2]} '
        #                                                    f'не получил послaние игрока {player_name} - @{info[0][2]} '
        #                                                    f'c пожеланием «{player_wish}» 🥺 '
        #                                                    f'Сообщи устно и проследи, чтобы {player_name} и подарок встретились!')
        #
        #         # меняем статус розыгрыша raffle на 1 !
        #         curs.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
        #                      {'raffle': 1, 'id': group_id[0][0]})
        #
        conn.commit()
        conn.close()

    else:
        # убить клавиатуру
        bot.send_message(message.chat.id, text='Санта не согласен!', reply_markup=ReplyKeyboardRemove())

    logmess(message)


# ВЫОЛНЕНИЕ РОЗЫГРЫША ТОЛЬКО В ПОСЛЕ ПОДТВЕРЖДЕНИЯ
def run_game(message):

    # message - это пришедший из кнопки group_id
    print(f'данные из обработки кнопок: {message}\n')

    conn = sqlite3.connect("santa.db")
    curs = conn.cursor()

    # берём id группы, leader_id и title по одному известному id группы (id, чтобы оперировать понятными названиями)
    curs.execute('SELECT id, leader_id, title FROM Groups WHERE id=:id', {'id': message})
    group_data = curs.fetchall()

    # как здесь вспомнить название выбранной для розыгрыша группы (title)
    # узнаём id выбранной группы (можно взять и БД-шный id для логов)
    # curs.execute('SELECT id FROM Groups WHERE title=:title', {'title': message.text})
    # group_id = curs.fetchall()
    #
    # print(f'Здесь id выбранной для розыгрыша группы: {group_id}')

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
    gr = message
    now = datetime.now()

    # складываем файлы логов розыгрыша в папку
    with open(os.path.join(os.path.dirname(__file__), 'logs', f'logs_{gr}.txt'), 'w') as log_list:
        log_list.write(f'group_id: {str(gr)}\n')
        log_list.write(f'run_game: {now}\n')
        log_list.write(f'leader tg_id: {group_data[0][1]}\n') # упадет?
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
        player_name = ''
        player_wish = ''

        if info[0][0] == None:
            player_name = info[0][1]
        elif info[0][1] == None:
            player_name = info[0][0]
        else:
            player_name = f'{info[0][0]} {info[0][1]}'

        if info[0][3] != None:
            player_wish = info[0][3]
        else:
            player_wish = 'не написано'

        # бот должен проверять доступность юзера перед отправкой, чтобы не падать
        print(f'santa_tg_id: {santa_tg_id[0][0]}')
        try:
            # отправляем информацию Санте!
            bot.send_message(santa_tg_id[0][0], text=f'☃️❄️☃️❄️☃️❄️☃️❄️☃️❄️️☃️️\n\n'
                                                     f'Привет! Вот и розыгрыш в группe «{group_data[0][2]}»! 🎉\n'
                                                     f'Ты будешь Тайным Сантой для человека по имени '
                                                     f'{player_name}! \n'
                                                     f'Его ник в телеграме: @{info[0][2]}.\n'
                                                     f'Его послание для тебя: {player_wish}.\n\n'
                                                     f'Ты можешь прислушаться к пожеланию по желанию 🎁\n\n'
                                                     f'Мира, любви, счастья, ура, чао-какао, я всё, до новых встреч!\n'
                                                     f'(Тексты мы, конечно, поправим...)\n\n'
                                                     f'🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄')
        except telebot.apihelper.ApiException:
            print('ветка исключений......')

            # узнаем данные Пропавшего Тайного Санты по значению его tg_id
            curs.execute('SELECT first_name, last_name, username FROM Users WHERE tg_id=:tg_id',
                         {'tg_id': santa_tg_id[0][0]})
            missing_santa = curs.fetchall()
            print(f'missing_santa: {missing_santa}')

            if missing_santa[0][0] == None:
                missing_santa_name = missing_santa[0][1]
            elif missing_santa[0][1] == None:
                missing_santa_name = missing_santa[0][0]
            else:
                missing_santa_name = f'{missing_santa[0][0]} {missing_santa[0][1]}'

            # узнаем tg_id ведущего по его бд_id
            print(f'leader_tg_id: {group_data[0][0]}')
            curs.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': group_data[0][1]})
            leader_tg_id = curs.fetchall()

            print(f'missing_santa: {missing_santa}')
            print(f'leader_tg_id: {leader_tg_id}')

            pl_wish = ''

            if player_wish == '':
                pl_wish = 'не написано'
            else:
                pl_wish = player_wish

            bot.send_message(leader_tg_id[0][0], text=f'🔴 Бедствие: пропавший Тайный Санта! 🔴 \n\n'
                                                   f'Игрок {missing_santa_name} - @{missing_santa[0][2]} '
                                                   f'не получил послaние игрока {player_name} - @{info[0][2]} '
                                                   f'c пожеланием «{pl_wish}» 🥺 \n\n'
                                                   f'Сообщи устно и проследи, чтобы {player_name} и подарок встретились!')

        # меняем статус розыгрыша raffle на 1 !
        curs.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
                     {'raffle': 1, 'id': group_data[0][0]})

    conn.commit()
    conn.close()


# обработка разных типов сообщений

# текст обрабатывается в ручном вводе названия группы
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