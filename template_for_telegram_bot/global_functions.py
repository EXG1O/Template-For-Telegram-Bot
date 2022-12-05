from database import DataBase

# Другое
import configparser
import os

def add_telegram_bot(db: DataBase, config: configparser.ConfigParser, telegram_bot_name: str, telegram_bot_token: str) -> str: # Функция для добавления Telegram ботов
	if db.get_data(table='TelegramBots', where=f"name='{telegram_bot_name}'", fetchone=True) == None:
		with open(f"{config['DEFAULT']['DataPath']}/config.ini", 'a') as config_file:
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
		with open(f"{config['DEFAULT']['DataPath']}/code_for_new_bots.txt", 'r') as code_for_new_bots_file:
			code_for_new_bots = code_for_new_bots_file.read()
		code_for_new_bots = telegram_bot_name.capitalize().join(code_for_new_bots.split('<-TelegramBotClassName->'))
		with open(f'./telegram_bot/{telegram_bot_name}/bot.py', 'w') as bot_file:
			bot_file.write(code_for_new_bots)

		return 'Вы успешно добавили Telegram бота.'
	else:
		return 'Telegram бот с таким именем уже создан!'

def delete_telegram_bot():
	pass

def add_superuser(db: DataBase, username: str) -> str: # Функция для добавления суперпользователя
	if db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True) == None:
		db.insert_into(table='Superusers', values=(len(db.get_data(table='Superusers', fetchall=True)) + 1, username))

		return 'Вы успешно добавили супер пользователья.'
	else:
		return 'Данный пользователь уже является супер пользователь!'

def delete_superuser():
	pass

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')