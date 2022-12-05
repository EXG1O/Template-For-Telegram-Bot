# Для работы класса Main
from database import DataBase
import global_functions as GlobalFunctions

# Другое
from threading import Thread, Lock
import configparser
import logging
import shutil
import sys
import os

# Класс Main
class Main:
	def __init__(self) -> None: # Инициализация класса Main
		print('*** Template For Telegram Bot ***')
		print('Автор: https://t.me/pycoder39\n')

		self.config = configparser.ConfigParser()
		self.if_file_not_find('./data', 'config.ini', '[DEFAULT]\nDataPath=./data\n\n[AdminTelegramBot]\nPrivate=1\nToken=None\n\n')
		self.config.read('data/config.ini')

		logging.basicConfig(filename=f"{self.config['DEFAULT']['DataPath']}/.log", filemode='a', level=logging.NOTSET, format="%(asctime)s - %(levelname)s: %(message)s")
		
		self.lock = Lock()
		self.db = DataBase(self.config, self.lock)
		self.db.create_table(table='TelegramBots', values='id INT NOT NULL, name TEXT PRIMARY KEY NOT NULL')
		self.db.create_table(table='Superusers', values='id INT NOT NULL, username TEXT PRIMARY KEY NOT NULL')
		if self.db.get_data(table='TelegramBots', where="name='admin'", fetchone=True) == None:
			self.db.insert_into(table='TelegramBots', values=(len(self.db.get_data(table='TelegramBots', fetchall=True)) + 1, 'admin'))
			self.db.create_table(table='AdminTelegramBotUsers', values="""
				user_id INT PRIMARY KEY NOT NULL,
				chat_id INT NOT NULL,
				username TEXT NOT NULL,
				reg_date TEXT NOT NULL,
				allowed_user INT NOT NULL
			""")

	def if_folder_not_find(self, path: str, folder: str) -> None: # Метод для создания файлов
		if folder not in os.listdir(path):
			os.mkdir(f'{path}/{folder}')

	def if_file_not_find(self, path: str, file: str, content: str) -> None: # Метод для создания папок
		if file not in os.listdir(path):
			with open(f'{path}/{file}', 'w') as f:
				f.write(content)

	def help(self) -> None: # Метод для вывода всех команд
		commands_list, num = '', 1
		for command in COMMANDS:
			commands_list += f"\n{num}. {command} - {COMMANDS[command]['comment']}"
			num += 1
		print(f'Список команд:{commands_list}')

	def start_telegram_bots(self) -> None: # Метод для запуска Telegram ботов
		if self.config['AdminTelegramBot']['Token'] == 'None':
			self.config['AdminTelegramBot']['Token'] = input(':: Введите Token Admin Telegram бота: ')
			with open('./data/config.ini', 'w') as config_file:
				self.config.write(config_file)
			self.config.read('data/config.ini')
		
		print('\nЗапуск Telegram ботов...')
		for telegram_bot in self.db.get_data(table='TelegramBots', fetchall=True):
			with open(f"{self.config['DEFAULT']['DataPath']}/code_for_start_bots.txt", 'r') as code_for_start_bots_file:
				code_for_start_bots = code_for_start_bots_file.read()
			code_for_start_bots = telegram_bot[1].capitalize().join(code_for_start_bots.split('<-TelegramBotClassName->'))
			code_for_start_bots = telegram_bot[1].join(code_for_start_bots.split('<-TelegramBotName->'))

			exec(code_for_start_bots)
		print('Все Telegram боты успешно запущено.')

	def add_telegram_bot(self) -> None: # Метод для добавления Telegram ботов
		telegram_bot_name = input(':: Придумайте имя Telegram боту (Например: Main): ').lower()
		telegram_bot_token = input (':: Введите Token Telegram бота: ')

		print('\nДобавления Telegram бота...')
		result = GlobalFunctions.add_telegram_bot(self.db, self.config, telegram_bot_name, telegram_bot_token)
		print(result)

	def add_superuser(self) -> None: # Метод для добавления суперпользователя
		print('Супер пользователь будет иметь доступ ко всем вашим Telegram ботам.')
		username = input(':: Введите @ пользователя: ')

		print('\nДобавления суперпользователя...')
		result = GlobalFunctions.add_superuser(self.db, username)
		print(result)

	def all_clear(self) -> None: # Метод для очистки всех созданных файлов
		print('Очистка...')
		for file in os.listdir(self.config['DEFAULT']['DataPath']):
			if file not in ['code_for_new_bots.txt', 'code_for_start_bots.txt']:
				os.remove(f"{self.config['DEFAULT']['DataPath']}/{file}")
		
		for folder in os.listdir('./telegram_bot'):
			if folder not in ['admin', 'keyboard.py']:
				shutil.rmtree(f'./telegram_bot/{folder}')
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
			'add_superuser': {
				'comment': 'Добавления суперпользователя;',
				'execute': main.add_superuser
			},
			'all_clear': {
				'comment': 'Удаление всех ваших Telegram ботов.',
				'execute': main.all_clear
			}
		}
		if sys.argv[1] in COMMANDS:
			COMMANDS[sys.argv[1]]['execute']()
		else:
			raise Exception('Команда не найдена!')
	else:
		raise Exception('Вы не указали команду!')
