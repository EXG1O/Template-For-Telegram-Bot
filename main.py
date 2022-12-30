import scripts.functions as GlobalFunctions
from scripts.variables import Variables
from scripts.database import DataBase

import logging
import shutil
import sys
import os

# Класс Main
class Main:
	def pre_setup(func) -> None: # Декоратор для предварительной настройки
		def wrapper(self):
			self.config = Variables().config
			if 'config.ini' not in os.listdir('./data'):
				with open('./data/config.ini', 'w') as config_file:
					config_file.write('[AdminTelegramBot]\nPrivate=1\nToken=None\n')
			self.config.read('./data/config.ini')

			self.db = DataBase()
			self.db.create_table(table='TelegramBots', values='id INT NOT NULL, name TEXT PRIMARY KEY NOT NULL')
			self.db.create_table(table='Superusers', values='id INT NOT NULL, username TEXT PRIMARY KEY NOT NULL')
			if self.db.get_data(table='TelegramBots', where="name='admin'", fetchone=True) == None:
				self.db.insert_into(table='TelegramBots', values=(1, 'admin'))
				self.db.create_table(table='AdminTelegramBotUsers', values="""
					user_id INT PRIMARY KEY NOT NULL,
					chat_id INT NOT NULL,
					username TEXT NOT NULL,
					reg_date TEXT NOT NULL,
					allowed_user INT NOT NULL
				""")

			func(self)
		wrapper.__name__ = func.__name__
		return wrapper

	def help(self) -> None: # Метод для вывода всех команд
		commands_list, num = '', 1
		for command in COMMANDS:
			commands_list += f"\n{num}. {command} - {COMMANDS[command]['comment']}"
			num += 1
		print(f'Список команд:{commands_list}')

	@pre_setup
	def start_telegram_bots(self) -> None: # Метод для запуска Telegram ботов
		if self.config['AdminTelegramBot']['Token'] == 'None':
			self.config['AdminTelegramBot']['Token'] = input(':: Введите токен Admin Telegram бота: ')
			with open('./data/config.ini', 'w') as config_file:
				self.config.write(config_file)
			self.config.read('data/config.ini')
			
			print('\nДля того, чтобы вы могли пользоваться Admin Telegram ботом, добавьте себя в список суперпользователей!')
			self.add_superuser()
			print()

		print('Запуск Telegram ботов...')
		logging.basicConfig(filename='./data/.log', filemode='a', level=logging.NOTSET, format="%(asctime)s - %(levelname)s: %(message)s")
		for telegram_bot in self.db.get_data(table='TelegramBots', fetchall=True):
			result = GlobalFunctions.start_telegram_bot(telegram_bot_name=telegram_bot[1])
			print(result)

	@pre_setup
	def add_telegram_bot(self) -> None: # Метод для добавления Telegram ботов
		telegram_bot_name = input(':: Придумайте имя Telegram боту: ').lower()
		telegram_bot_token = input (':: Введите Token Telegram бота: ')

		print('\nДобавления Telegram бота...')
		result = GlobalFunctions.add_telegram_bot(telegram_bot_name=telegram_bot_name, telegram_bot_token=telegram_bot_token)
		print(result)

	@pre_setup
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

	@pre_setup
	def add_superuser(self) -> None: # Метод для добавления суперпользователя
		print('Супер пользователь будет иметь доступ ко всем вашим Telegram ботам!')
		username = input(':: Введите @ пользователя: ')

		print('\nДобавления суперпользователя...')
		result = GlobalFunctions.add_superuser(username=username)
		print(result)

	@pre_setup
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
			if _file in ['.log', 'config.ini', 'DataBase.db']:
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
		raise Exception('Вы не указали команду!')
