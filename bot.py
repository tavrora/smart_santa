# -*- coding: utf-8 -*-

# import config
import telebot
import re
from idlelib import query
from datetime import datetime
from telebot import (apihelper, types)
from telebot.types import ReplyKeyboardRemove

from config import (token, socks5)

apihelper.proxy = {'https': socks5}
bot = telebot.TeleBot(token)
print("сервер работает...")
user = bot.get_me()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        start_param = message.text.split()
        if len(start_param) == 1:
            print("нет параметра запуска")
            bot.send_message(message.chat.id, "Привет! Я Санта-бот, помогу провести новогодний розыгрыш подарков в вашей компании!")
            keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура шириной в 2 кнопи в ряду
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
            keyboard.add(key_yes, key_no)  # добавляем кнопки в клавиатуру в один ряд
            # keyboard.add(key_no) # добавлять по одной кнопке в ряд
            question = "Хочешь создать новую группу для розыгрыша?"
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
            # bot.register_next_step_handler(message, new_group)
        else:
            print("есть параметр запуска")
            bot.send_message(message.chat.id, "Привет! Я Санта-бот и ты пришел ко мне по приглашению! Для твоего подарка уже есть место под ёлкой!")
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes1')
            key_no = types.InlineKeyboardButton(text='Нет', callback_data='no1')
            keyboard.add(key_yes, key_no)
            question = "Готов принять участие в розыгрыше?"
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "пиши привет в приват")
    log(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes': #call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, text="(будет запрос названия и генерация ссылки)")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None) # скрывает клаву после выбора
        # код сохранения данных, или их обработки
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, "ок. присоединись к своей группе по ссылке от ведущего")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None) # скрывает клаву после выбора
    elif call.data == 'yes1':
        bot.send_message(call.message.chat.id, "(потом спрошу у тебя имя)")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    elif call.data == 'no1':
        bot.send_message(call.message.chat.id, "Если передумаешь, набери команду /participate")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, "Помоги себе сам, я пишу другой функционал")
    else:
        bot.send_message(message.chat.id, "пиши привет в приват")
    log(message)

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


def log(message):
    print(f"\nmessage: {message}") # можно убрать этот вывод
    print("\n***")
    print(datetime.now())
    print(f"{message.chat.first_name} {message.chat.last_name} "
          f"({message.chat.username} id={message.chat.id}) пишет:\n{message.text}\n")


print("точно работает...")
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0, timeout=20) # какое время ожидания ставить, чтобы бот не выключался без сообщений

print("сервер выключен...")