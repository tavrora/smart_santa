# -*- coding: utf-8 -*-
import sqlite3

class Sqlighter:

    def __init__(self, database_name):
        # как передать имя БД через переменную?
        self.connection = sqlite3.connect('santa.db')
        self.cursor = self.connection.cursor()


    def select_group_by_start_parameter(self, start_parameter):
        """ Выбираем группу по параметру запуска """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Groups WHERE link=:link',
                                       {'link': start_parameter}).fetchall()


    def select_title_group_by_id (self, group_id):
        """ Узнаём название группы, по id группы """
        with self.connection:
            return self.cursor.execute('SELECT title FROM Groups '
                                       'WHERE id=:id', {'id': group_id}).fetchall()


    def select_active_groups_with_same_name (self, leader_id, title):
        """ Ищем активные группы ведущего с таким же названием (по id ведущего, названию группы, статусу розыгрыша"""
        with self.connection:
            return self.cursor.execute('SELECT * FROM Groups '
                                       'WHERE leader_id=:leader_id and title=:title and raffle=:raffle',
                                       {'leader_id': leader_id, 'title': title, 'raffle': 0}).fetchall()


    def select_user_by_tg_id (self, telegram_id):
        """ Выбираем пользователя по его телеграм id """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Users WHERE tg_id=:tg_id',
                                       {'tg_id': telegram_id}).fetchall()


    def insert_new_user (self, tg_id, username, first_name, last_name, current_group):
        """ Заносим нового пользователя в БД """
        with self.connection:
            self.cursor.execute('INSERT INTO Users(tg_id, username, first_name, last_name, current_group) '
                                 'VALUES (:tg_id, :username, :first_name, :last_name, :current_group)',
                                 {'tg_id': tg_id, 'username': username,
                                  'first_name': first_name, 'last_name': last_name,
                                  'current_group': current_group})
        return


    def update_user_info (self, username, first_name, last_name, current_group, tg_id,):
        """ Обновляем информацию пользователя в БД """
        with self.connection:
            self.cursor.execute('UPDATE Users SET username=:username, first_name=:first_name, '
                                'last_name=:last_name, current_group=:current_group '
                                 'WHERE tg_id=:tg_id', {'username': username,
                                  'first_name': first_name, 'last_name': last_name,
                                  'current_group': current_group, 'tg_id': tg_id})
        return


    def select_rel_user_with_group (self, user_id, group_id):
        """ Выбираем связь пользователя с группой """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Relations_user_group '
                                       'WHERE user_id=:user_id AND group_id=:group_id',
                                       {'user_id': user_id, 'group_id': group_id}).fetchall()


    def insert_rel_user_with_group (self, user_id, group_id):
        """ Устанавливаем связь пользователя и группы """
        with self.connection:
            self.cursor.execute('INSERT INTO Relations_user_group(user_id, group_id) '
                                 'VALUES (:user_id, :group_id)',
                                 {'user_id': user_id, 'group_id': group_id})
        return


    def update_status_participation_to_1 (self, user_id, group_id):
        """ Mеняем статус участия на 1 в таблице связей (подтверждение участия) """
        with self.connection:
            self.cursor.execute('UPDATE Relations_user_group SET participation=:participation '
                                'WHERE user_id=:user_id AND group_id=:group_id',
                                {'participation': 1, 'user_id': user_id, 'group_id': group_id}).fetchall()
        return


    def update_status_participation_to_0 (self, user_id, group_id):
        """ Mеняем статус участия на 0 в таблице связей (отмена участия) """
        with self.connection:
            self.cursor.execute('UPDATE Relations_user_group SET participation=:participation '
                                'WHERE user_id=:user_id AND group_id=:group_id',
                                {'participation': 0, 'user_id': user_id, 'group_id': group_id}).fetchall()
        return


    def update_wish (self, wish, user_id, group_id):
        """ Заносим/меняем пожелание в таблице связей """
        with self.connection:
            self.cursor.execute('UPDATE Relations_user_group SET wish=:wish '
                                'WHERE user_id=:user_id AND group_id=:group_id',
                                {'wish': wish, 'user_id': user_id, 'group_id': group_id}).fetchall()
        return


    def update_group_description (self, description, link):
        """ Заносим описание группы """
        with self.connection:
            self.cursor.execute('UPDATE Groups SET description=:description WHERE link=:link',
                                {'description': description, 'link': link}).fetchall()
        return


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()


    def unname (self, param):
        """ to do """
        with self.connection:
            return self.cursor.execute().fetchall()



    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()