# -*- coding: utf-8 -*-

# import config
import os
import telebot
import sqlite3
import re
from idlelib import query
from datetime import datetime
from telebot import (apihelper, types)
# from config import (token, socks5)
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
            # устанавливаем соединение с БД (объект соединения) - не закрываю нигде
            conn = sqlite3.connect("santa.db")
            # создаем объект Cursor для работы с его методом execute()
            curs = conn.cursor()
            # создаем связь с группой, если она существует иначе ссылка недействительна
            curs.execute('SELECT * FROM Groups WHERE link=:link', {'link': start_param[1]})
            group_exists = curs.fetchall()
            print(f'есть группа: {group_exists}')
            print(f'статус розыгрыша: raffle = {group_exists[0][3]}')
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
                # ??? else - НАДО ЛИ ИНАЧЕ ДЕЛАТЬ UPDATE НА СЛУЧАЙ ТОГО, ЧТО ПОЛЬЗОВАТЕЛЬ МЕНЯЛ СВОИ ДАННЫЕ (ИМЯ, ФАМИЛИЮ, USERNAME)
                # или зашел по другой ссылке?
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

                # устанавливаем связь пользователя и группы, ECЛИ ЕЁ ЕЩЁ НЕТ (пользователь перешел по ссылке впервые)
                curs.execute('SELECT * FROM Relations_user_group WHERE user_id=:user_id AND group_id=:group_id',
                             {'user_id': user_id[0][0], 'group_id': group_exists[0][0]})
                relation_exists = curs.fetchall()
                print(f'есть связь: {relation_exists}')
                if len(relation_exists) == 0:
                    curs.execute('INSERT INTO Relations_user_group(user_id, group_id) '
                                 'VALUES (:user_id, :group_id)',
                                 {'user_id': user_id[0][0], 'group_id': group_exists[0][0]})
                conn.commit()
                curs.close()

                bot.send_message(message.chat.id, text='Привет! Я Санта-бот и ты пришел ко мне по приглашению! '
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
            # сохраняем изменения
            conn.commit()
            # закрываем соединение cursor
            curs.close()

    else:
        bot.send_message(message.chat.id, 'Упс. Санта-бот работает только в режиме тет-а-тет.')
    logmess(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes_group':
        # скрываем клаву после выбора
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        get_group_name(call.message)
        # код сохранения данных, или их обработки
    elif call.data == 'no_group':
        bot.send_message(call.message.chat.id, text='ок. /newgroup если передумаешь или присоединяйся '
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
        curs.close()
        bot.send_message(call.message.chat.id, text='(потом спрошу у тебя пожелание)')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

    elif call.data == 'no_part':
        bot.send_message(call.message.chat.id, text='Если передумаешь, набери команду /participate.')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    logcall(call)


def get_group_name(message): # получаем название группы
    bot.send_message(message.chat.id, text='Напиши название группы и я пришлю тебе ссылку-приглашение. '
                                           'Название не должно начинаться со слеша.')
    bot.register_next_step_handler(message, link_generation)
    logmess(message)

def link_generation(message):  # генерируем ссылку после получения названия
    print(message.text[0])
    # проверяем, что введено название, а не команда
    if message.text[0] == '/':
        bot.send_message(message.chat.id, text='Проказник! Это не подходит для названия группы. '
                                               'Перейди по /newgroup, чтобы создать новую группу в будущем.'
                                               'Название должно быть уникально в рамках твоих активных групп.')
    else:
        # генерация ссылки тут
        # всех в БД! юзер-ведущий,  название группы, сгенеренная ссылка,
        bot.send_message(message.chat.id, text=f'Годится-ягодица! Группа "{message.text}" создана! '
                                               f'Вот ссылка-приглашение на участие для твоих друзей: '
                                               f'[https://telegram.me/shanta_bot?start=olololo]. '
                                               f'Если хочешь участвовать сам, перейди по ней и следуй '
                                               f'дальнейшим инструкциям. После регистрации всех желающих '
                                               f'ты можешь запустить розыгрыш командой /rungame.')
        # bot.send_message(message.chat.id, text='Будь любезен, для участия в этом розыгрыше перейди на /participate')
        # далее логика регистрации на участие
    logmess(message)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, text='/start - запустить бота\n'
                                               '/help - получить помощь\n'
                                               '/newgroup - создать новую группу для розыгрыша (*)\n'
                                               '/participate - принять участие в розыгрыше (*)\n'
                                               '/leaveroup - выйти из розыгрыша (*)\n'
                                               '/enterwish - ввести или редактировать пожелание (*)\n'
                                               '/rungame - запустить розыгрыш (для ведущего) (*)')
    else:
        bot.send_message(message.chat.id, text='Упс. Санта-бот работает только в режиме тет-а-тет.')
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