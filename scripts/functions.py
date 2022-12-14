from scripts.variables import Variables
from scripts.database import DataBase

from threading import Thread
import cryptocode
import shutil
import os

def start_telegram_bot(telegram_bot_name: str): # Функция для запуска Telegram бота
	with open('./data/code_for_start_bot.py', 'r') as code_for_start_bot_file:
		code_for_start_bot = code_for_start_bot_file.read()
	code_for_start_bot = telegram_bot_name.capitalize().join(code_for_start_bot.split('Template'))
	code_for_start_bot = telegram_bot_name.join(code_for_start_bot.split('template'))

	try:
		exec(code_for_start_bot)
		return f'{telegram_bot_name.capitalize()} Telegram бот успешно запущен.'
	except Exception as exception:
		return f'Не удалось запустить {telegram_bot_name.capitalize()} Telegram бота!\nОшибка: {exception}'

def get_db(func): # Декоратор для получения db аргумента
	def wrapper(*args, **kwargs):
		kwargs.update({'db': DataBase()})
		return func(*args, **kwargs)
	wrapper.__name__ = func.__name__
	return wrapper

@get_db
def add_telegram_bot(db: DataBase, telegram_bot_name: str, telegram_bot_token: str) -> str: # Функция для добавления Telegram ботов
	telegram_bot_name = '_'.join(telegram_bot_name.lower().split())

	NOT_ALLOWED_SYMBOLS = [
		'`', '~', '!', '@', '#', '$',
		'%', '^', '&', '*', '(', ')',
		'-', '–', '—', '=', '+', '[',
		']', '{', '}', ';', ':', "'",
		'"', ',', '.', '/', '<', '>',
		'?', '|', '§', '°'
	]
	allowed_telegram_bot_name = ''
	for symbol in telegram_bot_name:
		if symbol not in NOT_ALLOWED_SYMBOLS:
			allowed_telegram_bot_name += symbol
	telegram_bot_name = allowed_telegram_bot_name
	
	if db.get_data(table='TelegramBots', where=f"name='{telegram_bot_name}'", fetchone=True) == None:
		db.insert_into(table='TelegramBots', values=(len(db.get_data(table='TelegramBots', fetchall=True)) + 1, telegram_bot_name, cryptocode.encrypt(telegram_bot_token, Variables.unique_key), 1))
		values = """
			user_id INT PRIMARY KEY NOT NULL,
			chat_id INT NOT NULL,
			username TEXT NOT NULL,
			reg_date TEXT NOT NULL,
			allowed_user INT NOT NULL
		"""
		db.create_table(table=f'{telegram_bot_name.capitalize()}TelegramBotUsers', values=values)

		os.mkdir(f'./telegram_bots/{telegram_bot_name}')
		with open('./data/code_for_new_bot.py', 'r') as code_for_new_bot_file:
			code_for_new_bot = code_for_new_bot_file.read()
		code_for_new_bot = telegram_bot_name.capitalize().join(code_for_new_bot.split('Template'))
		with open(f'./telegram_bots/{telegram_bot_name}/bot.py', 'w') as bot_file:
			bot_file.write(code_for_new_bot)

		return f'Вы успешно добавили {telegram_bot_name} Telegram бота.'
	else:
		return 'Telegram бот с таким именем уже создан!'

@get_db
def delete_telegram_bot(db: DataBase, telegram_bot_id: int) -> str | tuple: # Функция для удаления Telegram бота
	telegram_bot_name: str = db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

	if telegram_bot_name != 'admin':
		db.delete_record(table='TelegramBots', where=f"id='{telegram_bot_id}'")
		shutil.rmtree(f'./telegram_bots/{telegram_bot_name}')
		db.drop_table(table=f'{telegram_bot_name.capitalize()}TelegramBotUsers')

		return f'Вы успешно удалили {telegram_bot_name.capitalize()} Telegram бота.'
	else:
		return 'Нельзя удалять Admin Telegram бота!'

@get_db
def add_superuser(db: DataBase, username: str) -> str: # Функция для добавления суперпользователя
	if username.find('@') != -1:
		if db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True) == None:
			db.insert_into(table='Superusers', values=(len(db.get_data(table='Superusers', fetchall=True)) + 1, username))

			return f'Вы успешно добавили суперпользователья {username}.'
		else:
			return f'Пользователь {username} уже является суперпользователем!'
	else:
		return 'Вы неверно ввели @ пользователя!'

@get_db
def delete_superuser(db: DataBase, superuser_id: int) -> str: # Функция для удаления суперпользователя
	username: str = db.get_data(table='Superusers', where=f'id={superuser_id}', fetchone=True)[1]
	
	db.delete_record(table='Superusers', where=f'id={superuser_id}')
	
	return f'Вы успешно удалили суперпользователя {username}.'

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')