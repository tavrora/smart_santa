# -*- coding: utf-8 -*-
import sqlite3

class Sqlighter:

    def __init__(self, database_name):
        # как передать имя БД через переменную?
        self.connection = sqlite3.connect('santa.db')
        self.cursor = self.connection.cursor()


    def insert_new_group (self, title, link, leader_id):
        """ Заносим новую группу в БД """
        with self.connection:
             self.cursor.execute('INSERT INTO Groups(title, link, raffle, leader_id)'
                                 'VALUES (:title, :link, :raffle, :leader_id)',
                                 {'title': title, 'link': link,
                                  'raffle': 0, 'leader_id': leader_id}).fetchall()
        return


    def update_group_description (self, description, link):
        """ Заносим описание группы """
        with self.connection:
            self.cursor.execute('UPDATE Groups SET description=:description WHERE link=:link',
                                {'description': description, 'link': link}).fetchall()
        return


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


    def select_id_tit_lead_group_by_id (self, group_id):
        """ Берём данные группы (id, название, ведущего) по id группы """
        with self.connection:
            return self.cursor.execute('SELECT id, title, leader_id FROM Groups '
                                       'WHERE id=:id', {'id': group_id}).fetchall()


    def select_title_active_user_groups (self, leader_id):
        """ Выбираем названия всех активных групп ведущего """
        with self.connection:
            return self.cursor.execute('SELECT title FROM Groups WHERE leader_id=:leader_id AND raffle=:raffle',
                                       {'leader_id': leader_id, 'raffle': 0}).fetchall()


    def select_active_groups_with_same_name (self, leader_id, title):
        """ Ищем активные группы ведущего с таким же названием (по id ведущего, названию группы, статусу розыгрыша"""
        with self.connection:
            return self.cursor.execute('SELECT * FROM Groups '
                                       'WHERE leader_id=:leader_id and title=:title and raffle=:raffle',
                                       {'leader_id': leader_id, 'title': title, 'raffle': 0}).fetchall()


    def select_id_active_groups_by_title (self, title):
        """ Узнаём id активной группы ведущего по названию """
        with self.connection:
            return self.cursor.execute('SELECT id FROM Groups WHERE title=:title AND raffle=:raffle',
                                       {'title': title, 'raffle': 0}).fetchall()


    def update_status_raffle_to_1 (self, group_id):
        """ Mеняем статус розыгрыша на 1 (после розыгрыша) """
        with self.connection:
            self.cursor.execute('UPDATE Groups SET raffle=:raffle WHERE id=:id',
                                {'raffle': 1, 'id': group_id}).fetchall()
        return



    def insert_new_user (self, tg_id, username, first_name, last_name, current_group):
        """ Заносим нового пользователя в БД """
        with self.connection:
            self.cursor.execute('INSERT INTO Users(tg_id, username, first_name, last_name, current_group) '
                                 'VALUES (:tg_id, :username, :first_name, :last_name, :current_group)',
                                 {'tg_id': tg_id, 'username': username,
                                  'first_name': first_name, 'last_name': last_name,
                                  'current_group': current_group})
        return


    def select_user_by_tg_id (self, tg_id):
        """ Выбираем пользователя по его телеграм id """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Users WHERE tg_id=:tg_id',
                                       {'tg_id': tg_id}).fetchall()


    def select_missing_santa_data_by_tg_id (self, tg_id):
        """ Узнаём данные Пропавшего Тайного Санты по значению его tg_id """
        with self.connection:
            return self.cursor.execute('SELECT first_name, last_name, username FROM Users '
                                       'WHERE tg_id=:tg_id',
                                       {'tg_id': tg_id}).fetchall()


    def select_tg_id_user_by_db_id (self, id):
        """ Узнаём телеграм id ведущего по его бд id"""
        with self.connection:
            return self.cursor.execute('SELECT tg_id FROM Users WHERE id=:id', {'id': id}).fetchall()


    def update_user_info (self, username, first_name, last_name, current_group, tg_id,):
        """ Обновляем информацию пользователя в БД """
        with self.connection:
            self.cursor.execute('UPDATE Users SET username=:username, first_name=:first_name, '
                                'last_name=:last_name, current_group=:current_group '
                                 'WHERE tg_id=:tg_id', {'username': username,
                                  'first_name': first_name, 'last_name': last_name,
                                  'current_group': current_group, 'tg_id': tg_id})
        return



    def insert_rel_user_with_group (self, user_id, group_id, participation):
        """ Устанавливаем связь пользователя и группы с переданным статусом участия"""
        with self.connection:
            self.cursor.execute('INSERT INTO Relations_user_group(user_id, group_id, participation) '
                                 'VALUES (:user_id, :group_id, :participation)',
                                 {'user_id': user_id, 'group_id': group_id, 'participation': participation})
        return


    def select_rel_user_with_group (self, user_id, group_id):
        """ Выбираем связь пользователя с группой """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Relations_user_group '
                                       'WHERE user_id=:user_id AND group_id=:group_id ',
                                       {'user_id': user_id, 'group_id': group_id}).fetchall()


    def select_participants_in_active_group (self, group_id):
        """ Проверяем наличие участников в активной группе """
        with self.connection:
            return self.cursor.execute('SELECT * FROM Relations_user_group WHERE group_id=:group_id '
                                       'AND participation=:participation',
                                       {'group_id': group_id, 'participation': 1}).fetchall()


    def select_participants_in_group_to_run (self, group_id):
        """ Выбираем id всех участников в группе розыгрыша """
        with self.connection:
            return self.cursor.execute('SELECT user_id FROM Relations_user_group '
                                       'WHERE group_id=:group_id AND participation=:participation',
                                       {'group_id': group_id, 'participation': 1}).fetchall()


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


    def select_participant_data_for_Sant (self, user_id, group_id):
        """ Выбираем все необходимые данные участников для Сант """
        with self.connection:
            return self.cursor.execute('SELECT us.first_name, us.last_name, us.username, rel.wish '
                                       'FROM Users as us '
                                       'LEFT JOIN Relations_user_group as rel '
                                       'ON us.id = rel.user_id '
                                       'WHERE user_id=:user_id AND group_id=:group_id',
                                       {'user_id': user_id, 'group_id': group_id}).fetchall()


    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()