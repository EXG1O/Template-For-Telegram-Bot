# Для работы скрипта
from database import DataBase

# Другое
import configparser
import shutil
import os

def add_telegram_bot(db: DataBase, config: configparser.ConfigParser, telegram_bot_name: str, telegram_bot_token: str) -> str: # Функция для добавления Telegram ботов
	if db.get_data(table='TelegramBots', where=f"name='{telegram_bot_name}'", fetchone=True) == None:
		with open('./data/config.ini', 'a') as config_file:
			config_file.write(f'[{telegram_bot_name.capitalize()}TelegramBot]\nPrivate=1\nToken={telegram_bot_token}\n\n')

		db.insert_into(table='TelegramBots', values=(len(db.get_data(table='TelegramBots', fetchall=True)) + 1, telegram_bot_name))
		values = """
			user_id INT PRIMARY KEY NOT NULL,
			chat_id INT NOT NULL,
			username TEXT NOT NULL,
			reg_date TEXT NOT NULL,
			allowed_user INT NOT NULL
		"""
		db.create_table(table=f'{telegram_bot_name.capitalize()}TelegramBotUsers', values=values)

		os.mkdir(f'./telegram_bot/{telegram_bot_name}')
		with open('./data/code_for_new_bots.txt', 'r') as code_for_new_bots_file:
			code_for_new_bots = code_for_new_bots_file.read()
		code_for_new_bots = telegram_bot_name.capitalize().join(code_for_new_bots.split('<-TelegramBotClassName->'))
		with open(f'./telegram_bot/{telegram_bot_name}/bot.py', 'w') as bot_file:
			bot_file.write(code_for_new_bots)

		return 'Вы успешно добавили Telegram бота.'
	else:
		return 'Telegram бот с таким именем уже создан!'

def delete_telegram_bot(db: DataBase, config: configparser.ConfigParser, telegram_bot_id: int) -> str | tuple: # Функция для удаления Telegram бота
	telegram_bot_name: str = db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

	if telegram_bot_name != 'admin':
		db.delete_record(table='TelegramBots', where=f"id='{telegram_bot_id}'")
		shutil.rmtree(f'./telegram_bot/{telegram_bot_name}')

		with open('./data/config.ini', 'r') as config_file:
			config_str = config_file.read()
			lines = config_str.split('\n')

		num = 0
		for line in lines:
			if line == f'[{telegram_bot_name.capitalize()}TelegramBot]':
				break
			num += 1

		for i in range(4):
			del lines[num]
		config_str = '\n'.join(lines)

		with open('./data/config.ini', 'w') as config_file:
			config_file.write(config_str)

		return f'Вы успешно удалили {telegram_bot_name.capitalize()} Telegram бота.'
	else:
		return 'Нельзя удалять Admin Telegram бота!'

def add_superuser(db: DataBase, username: str) -> str: # Функция для добавления суперпользователя
	if username.find('@') != -1:
		if db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True) == None:
			db.insert_into(table='Superusers', values=(len(db.get_data(table='Superusers', fetchall=True)) + 1, username))

			return f'Вы успешно добавили суперпользователья {username}.'
		else:
			return f'Пользователь {username} уже является суперпользователем!'
	else:
		return 'Вы неверно ввели @ пользователя!'

def delete_superuser(db: DataBase, superuser_id: int) -> str: # Функция для удаления суперпользователя
	username: str = db.get_data(table='Superusers', where=f'id={superuser_id}', fetchone=True)[1]
	
	db.delete_record(table='Superusers', where=f'id={superuser_id}')
	
	return f'Вы успешно удалили суперпользователя {username}.'

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')