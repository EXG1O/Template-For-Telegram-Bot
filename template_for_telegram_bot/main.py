from threading import Thread
import configparser
import logging
import sqlite3
import shutil
import sys
import os

class Main:
	def __init__(self) -> None:
		print('*** Template For Telegram Bot ***')
		print('Автор: https://t.me/pycoder39\n')

		self.if_file_not_find('./data', 'config.ini', '[DEFAULT]\nDataPath=./data\n\n[AdminTelegramBot]\nPrivate=1\nToken=None\n\n')

		self.config = configparser.ConfigParser()
		self.config.read('data/config.ini')

		logging.basicConfig(filename=f"{self.config['DEFAULT']['DataPath']}/.log", filemode='a', level=logging.NOTSET, format="%(asctime)s - %(levelname)s: %(message)s")

		self.db = sqlite3.connect(f"{self.config['DEFAULT']['DataPath']}/DataBase.db")
		self.sql = self.db.cursor()

		self.sql.execute(f"""
			CREATE TABLE IF NOT EXISTS TelegramBots (
				id INT PRIMARY KEY NOT NULL,
				name TEXT NOT NULL
			)
		""")
		self.db.commit()

		self.sql.execute("SELECT * FROM TelegramBots WHERE name='admin'")
		if self.sql.fetchone() == None:
			self.sql.execute("SELECT * FROM TelegramBots")
			telegram_bots = self.sql.fetchall()
			self.sql.execute("INSERT INTO TelegramBots VALUES (?, ?)", (len(telegram_bots) + 1, 'admin'))
			self.db.commit()

	def if_folder_not_find(self, path: str, folder: str) -> None:
		if folder not in os.listdir(path):
			os.mkdir(f'{path}/{folder}')

	def if_file_not_find(self, path: str, file: str, content: str) -> None:
		if file not in os.listdir(path):
			with open(f'{path}/{file}', 'w') as f:
				f.write(content)

	def start_telegram_bots(self) -> None:
		if self.config['AdminTelegramBot']['Token'] == 'None':
			self.config['AdminTelegramBot']['Token'] = input(':: Введите Token Admin Telegram бота: ')
			with open('./data/config.ini', 'w') as config_file:
				self.config.write(config_file)
			self.config.read('data/config.ini')
		
		print('\nЗапуск Telegram ботов...')
		for telegram_bot in self.sql.execute("SELECT * FROM TelegramBots"):
			telegram_bot_name = telegram_bot[1]
			with open(f"{self.config['DEFAULT']['DataPath']}/code_for_start_bots.txt", 'r') as code_for_start_bots_file:
				code_for_start_bots = code_for_start_bots_file.read()
			code_for_start_bots = telegram_bot_name.capitalize().join(code_for_start_bots.split('<-TelegramBotClassName->'))
			code_for_start_bots = telegram_bot_name.join(code_for_start_bots.split('<-TelegramBotName->'))
			exec(code_for_start_bots)
		print('Все Telegram боты успешно запущено.')

	def add_telegram_bot(self) -> None:
		telegram_bot_name = input(':: Придумайте имя Telegram боту (Например: Main): ').lower()
		telegram_bot_token = input (':: Введите Token Telegram бота: ')
		
		self.sql.execute(f"SELECT * FROM TelegramBots WHERE name='{telegram_bot_name}'")
		if self.sql.fetchone() == None:
			print('\nСоздание Telegram бота...')

			with open(f"{self.config['DEFAULT']['DataPath']}/config.ini", 'a') as config_file:
				config_file.write(f'[{telegram_bot_name.capitalize()}TelegramBot]\nPrivate=1\nToken={telegram_bot_token}\n\n')
			
			self.sql.execute("SELECT * FROM TelegramBots")
			telegram_bots = self.sql.fetchall()
			self.sql.execute("INSERT INTO TelegramBots VALUES (?, ?)", (len(telegram_bots) + 1, telegram_bot_name))
			self.sql.execute(f"""
				CREATE TABLE IF NOT EXISTS {telegram_bot_name.capitalize()}TelegramBotUsers (
					user_id INT PRIMARY KEY NOT NULL,
					chat_id INT NOT NULL,
					username TEXT NOT NULL,
					reg_date TEXT NOT NULL,
					allowed_user INT NOT NULL
				)
			""")
			self.db.commit()

			os.mkdir(f'./telegram_bot/{telegram_bot_name}')
			with open(f"{self.config['DEFAULT']['DataPath']}/code_for_new_bots.txt", 'r') as code_for_new_bots_file:
				code_for_new_bots = code_for_new_bots_file.read()
			code_for_new_bots = telegram_bot_name.capitalize().join(code_for_new_bots.split('<-TelegramBotClassName->'))
			with open(f'./telegram_bot/{telegram_bot_name}/bot.py', 'w') as bot_file:
				bot_file.write(code_for_new_bots)

			print('Успешное создание Telegram бота.')
		else:
			print('Telegram бот с таким именем уже создан!')

	def add_superuser(self) -> None:
		pass

	def all_clear(self) -> None:
		print('Очистка...')
		for file in os.listdir(self.config['DEFAULT']['DataPath']):
			if file not in ['code_for_new_bots.txt', 'code_for_start_bots.txt']:
				os.remove(f"{self.config['DEFAULT']['DataPath']}/{file}")
		
		for folder in os.listdir('./telegram_bot'):
			if folder not in ['admin', 'keyboard.py']:
				shutil.rmtree(f'./telegram_bot/{folder}')
		print('Успешная очистка.')

if __name__ == '__main__':
	main = Main()
	if sys.argv[1] == 'start':
		main.start_telegram_bots()
	elif sys.argv[1] == 'add_telegram_bot':
		main.add_telegram_bot()
	elif sys.argv[1] == 'add_superuser':
		main.add_superuser()
	elif sys.argv[1] == 'all_clear':
		main.all_clear()
	else:
		raise Exception('Команда не найдена!')
