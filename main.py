import scripts.functions as GlobalFunctions
from scripts.variables import Variables
from scripts.database import DataBase

import cryptocode
import random

import logging
import shutil
import sys
import os

# Класс Main
class Main:
	def __init__(self) -> None: # Инициализация класса Main
		self.db = DataBase()
		
		if 'unique.key' not in os.listdir('./data'):
			print(
				"""\
					Так как фреймворк был запущен впервые, создаём рандомный уникальный ключ для шифрования важных данных.
					Уникальный ключ будет в файле ./data/unique.key!
				
					Создания уникального ключа...""".replace('	', '')
			)
			
			unique_key =''
			for i in range(100):
				unique_key += random.choice('+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
			
			with open('./data/unique.key', 'w') as unique_key_file:
				unique_key_file.write(unique_key)

			Variables.unique_key = unique_key

			print(
				f"""\
					Успешное создание уникального ключа.
					Уникальный ключ: {unique_key}
				""".replace('	', '')
			)
		else:
			with open('./data/unique.key', 'r') as unique_key_file:
				Variables.unique_key = unique_key_file.read()
		
		self.db.create_table(table='TelegramBots', values="""
			id INT UNIQUE NOT NULL,
			name TEXT PRIMARY KEY NOT NULL,
			token TEXT UNIQUE NOT NULL,
			private INT NOT NULL
		""")
		self.db.create_table(table='Superusers', values="""
			id INT PRIMARY KEY NOT NULL,
			username TEXT UNIQUE NOT NULL
		""")
		if self.db.get_data(table='TelegramBots', where="name='admin'", fetchone=True) == None:
			self.db.insert_into(table='TelegramBots', values=(1, 'admin', 'None', 1))
			self.db.create_table(table='AdminTelegramBotUsers', values="""
				user_id INT PRIMARY KEY NOT NULL,
				chat_id INT NOT NULL,
				username TEXT NOT NULL,
				reg_date TEXT NOT NULL,
				allowed_user INT NOT NULL
			""")

	def help(self) -> None: # Метод для вывода всех команд
		commands_list, num = '', 1
		for command in COMMANDS:
			commands_list += f"\n{num}. {command} - {COMMANDS[command]['comment']}"
			num += 1
		print(f'Список команд:{commands_list}')

	def start_telegram_bots(self) -> None: # Метод для запуска Telegram ботов
		if self.db.get_data(table='TelegramBots', where="name='admin'", fetchone=True)[2] == 'None':
			admin_telegram_bot_token = input(':: Введите токен Admin Telegram бота: ')
			admin_telegram_bot_token_encoded = cryptocode.encrypt(admin_telegram_bot_token, Variables.unique_key)
			self.db.edit_value(table='TelegramBots', value=f"token='{admin_telegram_bot_token_encoded}'", where="name='admin'")
			
			print('\nДля того, чтобы вы могли пользоваться Admin Telegram ботом, добавьте себя в список суперпользователей!')
			self.add_superuser()
			print()

		print('Запуск Telegram ботов...')
		logging.basicConfig(filename='./data/.log', filemode='a', level=logging.NOTSET, format="%(asctime)s - %(levelname)s: %(message)s")
		for telegram_bot in self.db.get_data(table='TelegramBots', fetchall=True):
			result = GlobalFunctions.start_telegram_bot(telegram_bot_name=telegram_bot[1])
			print(result)

	def add_telegram_bot(self) -> None: # Метод для добавления Telegram ботов
		telegram_bot_name = input(':: Придумайте имя Telegram боту: ')
		telegram_bot_token = input (':: Введите Token Telegram бота: ')

		print('\nДобавления Telegram бота...')
		result = GlobalFunctions.add_telegram_bot(telegram_bot_name=telegram_bot_name, telegram_bot_token=telegram_bot_token)
		print(result)

	def delete_telegram_bot(self) -> None: # Метод для удаления Telegram бота
		telegram_bots: list = self.db.get_data('TelegramBots', fetchall=True)
		
		telegram_bots_list, num = 'Список ваших Telegram ботов:', 1
		for telegram_bot in telegram_bots:
			telegram_bots_list += f'\n{num}. {telegram_bot[1]}'
			num += 1
		telegram_bots_list += '\n\nВведите номер Telegram бота: '
		
		telegram_bot_num = input(telegram_bots_list)
		if telegram_bot_num.isdigit():
			if int(telegram_bot_num) <= len(telegram_bots):
				num = 1
				for telegram_bot in telegram_bots:
					if int(telegram_bot_num) == num:
						telegram_bot_id: int = telegram_bot[0]
						break
					num += 1

				print('\nУдаление Telegram бота...')
				result = GlobalFunctions.delete_telegram_bot(telegram_bot_id=telegram_bot_id)
				print(result)
			else:
				assert Exception('Такого номера Telegram бота нет в списке!')
		else:
			assert Exception('Вы ввели не число!')

	def add_superuser(self) -> None: # Метод для добавления суперпользователя
		print('Супер пользователь будет иметь доступ ко всем вашим Telegram ботам!')
		username = input(':: Введите @ пользователя: ')

		print('\nДобавления суперпользователя...')
		result = GlobalFunctions.add_superuser(username=username)
		print(result)

	def delete_superuser(self) -> None: # Метод для удаления суперпользователя
		superusers: list = self.db.get_data('Superusers', fetchall=True)
		
		if superusers != []:
			superusers_list, num = 'Список суперпользователей: ', 1
			for superuser in superusers:
				superusers_list += f'\n{num}. {superuser[1]}'
				num += 1
			superusers_list += '\n\nВведите номер суперпользователя: '
			
			superuser_num = input(superusers_list)
			if superuser_num.isdigit():
				if int(superuser_num) <= len(superusers):
					num = 1
					for superuser in superusers:
						if int(superuser_num) == num:
							superuser_id: int = superuser[0]
							break
						num += 1

					print('\nУдаление суперпользователя...')
					result = GlobalFunctions.delete_superuser(superuser_id=superuser_id)
					print(result)
				else:
					assert Exception('Такого номера суперпользователя нет в списке!')
			else:
				assert Exception('Вы ввели не число!')
		else:
			print('У вас нет ещё суперпользователей!')

	def clear(self) -> None: # Метод для очистки всех созданных файлов
		print('Очистка...')
		for _file in os.listdir('./data'):
			if _file in ['.log', 'DataBase.db']:
				os.remove(f'./data/{_file}')
		
		for folder in os.listdir('./telegram_bots'):
			if folder not in ['admin']:
				shutil.rmtree(f'./telegram_bots/{folder}')
		print('Успешная очистка.')

if __name__ == '__main__': # Проверка, как был запущен скрипт
	if len(sys.argv) > 1:
		main = Main()
		COMMANDS = {
			'help': {
				'comment': 'Вывод всех команд;',
				'execute': main.help
			},
			'start': {
				'comment': 'Запуск всех ваших Telegram ботов;',
				'execute': main.start_telegram_bots
			},
			'add_telegram_bot': {
				'comment': 'Добавления Telegram бота;',
				'execute': main.add_telegram_bot
			},
			'delete_telegram_bot': {
				'comment': 'Удаления Telegram бота;',
				'execute': main.delete_telegram_bot
			},
			'add_superuser': {
				'comment': 'Добавления суперпользователя;',
				'execute': main.add_superuser
			},
			'delete_superuser': {
				'comment': 'Удаления суперпользователя;',
				'execute': main.delete_superuser
			},
			'clear': {
				'comment': 'Удаление всех ваших Telegram ботов.',
				'execute': main.clear
			}
		}
		if sys.argv[1] in COMMANDS:
			COMMANDS[sys.argv[1]]['execute']()
		else:
			raise Exception('Команда не найдена!')
	else:
		raise Exception('Вы не ввели команду!')
