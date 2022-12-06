# Для работы Telegram бота
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram.ext
import telegram

# Для работы с клавиатурой и базой данных Telegram бота
import global_functions as GlobalFunctions
from telegram_bot.keyboard import Keyboard
from database import DataBase

# Другое
from configparser import ConfigParser
from datetime import datetime
from threading import Lock

# Класс AdminTelegramBot
class AdminTelegramBot:
	def __init__(self, config: ConfigParser, lock: Lock) -> None: # Инициализация класса AdminTelegramBot
		self.config = config

		self.db = DataBase(config, lock)

		self.wait_user_message = {}
		self.commands = {
			'start': self.start_command
		}
		self.callback = {
			'telegram_bots': self.telegram_bots, # 1
			'telegram_bot_settings': self.telegram_bot_settings, # 1:1
			'edit_telegram_bot_type': self.edit_telegram_bot_type, # 1:1:1
			'edit_telegram_bot_token': self.edit_telegram_bot_token, # 1:1:2
			'telegram_bot_users': self.telegram_bot_users, # 1:2
			'add_telegram_bot': self.add_telegram_bot, # 1:3
			'delete_telegram_bot': self.delete_telegram_bot, # 1:4
			'superusers': self.superusers, # 2
			'add_superuser': self.add_superuser, # 2:1
			'delete_superuser': self.delete_superuser, # 2:2
			'back_to_admin_menu': self.back_to_admin_menu, # 0
			'cancel_comand': self.cancel_comand # -1
		}

		self.admin_menu_kb = Keyboard(inline=True)
		self.admin_menu_kb.add_button([{'text': 'Список ваших Telegram ботов', 'callback_data': 'telegram_bots'}])
		self.admin_menu_kb.add_button([{'text': 'Суперпользователи', 'callback_data': 'superusers'}])

		self.back_to_admin_menu_kb = Keyboard(inline=True)
		self.back_to_admin_menu_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])

		self.cancel_comand_kb = Keyboard(inline=True)
		self.cancel_comand_kb.add_button([{'text': 'Отменить', 'callback_data': 'cancel_comand'}])

	def check_user(func) -> None: # Декоратор для проверки доступа пользователя к данному боту
		def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
			chat_id, user_id, username = update.effective_chat.id, update.effective_user.id, update.effective_user.name

			user: tuple | None = self.db.get_data(table='AdminTelegramBotUsers', where=f"user_id='{user_id}'", fetchone=True)
			superuser: tuple | None = self.db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True)
			if user == None:
				values = (
					user_id,
					chat_id,
					username,
					str(datetime.now()).split('.')[0],
					0 if self.config['AdminTelegramBot']['Private'] == '1' else 1
				)
				self.db.insert_into(table='AdminTelegramBotUsers', values=values)

				if superuser == None:
					self.config.read('./data/config.ini')
					if self.config['AdminTelegramBot']['Private'] == '1':
						context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, ожидайте пока вам разрешат им пользоваться.')
					else:
						context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, и можете пользоваться ботом.')

			if superuser == None:
				if user != None:
					self.config.read('./data/config.ini')
					if user[4] == 1 or self.config['AdminTelegramBot']['Private'] == '0':
						func(self, update, context)
					else:
						context.bot.send_message(chat_id=chat_id, text='Вы не имеете доступ к данному боту!')
			else:
				func(self, update, context)
		wrapper.__name__ = func.__name__
		return wrapper

	def get_user_data(arugments_list: list) -> None: # Декоратор для получения необходимой информации
		def decorator(func):
			def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
				arugments = {
					'update': update,
					'context': context,
					'user_id': update.effective_user.id,
					'chat_id': update.effective_chat.id,
					'username': update.effective_user.username,
					'message_id': update.effective_message.message_id
				}
				if update.callback_query != None:
					arugments.update({'callback_data': update.callback_query.data})

				arugments_dict = {'self': self}
				for arugment in arugments_list:
					if arugment in arugments:
						arugments_dict.update({arugment: arugments[arugment]})
				func(**arugments_dict)
			wrapper.__name__ = func.__name__
			return wrapper
		return decorator

	@check_user
	def handle_callback_query(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext) -> None: # Метод для обработки Callback
		callback_data = update.callback_query.data.split(':')[0]
		if callback_data in self.callback:
			self.callback[callback_data](update, context)
	
	@check_user
	@get_user_data(arugments_list=['update', 'context', 'user_id', 'chat_id'])
	def new_message(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int) -> None: # Метод для обработки сообщений
		message = update.effective_message.text
		
		if user_id in self.wait_user_message:
			data: list = self.wait_user_message[user_id].split(':')
			match data[0]:
				case 'edit_telegram_bot_token':
					message_id = int(data[1])
					telegram_bot_id = int(data[2])
					telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

					self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Token'] = message
					with open('./data/config.ini', 'w') as config_file:
						self.config.write(config_file)
					self.config.read('data/config.ini')

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					del self.wait_user_message[user_id]

					context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Теперь токен {telegram_bot_name.capitalize()} Telegram бота: <i>{message}</i>\n<b>Чтобы изменения вступили в силу, перезапустите файл main.py!</b>', parse_mode='HTML', reply_markup=self.back_to_admin_menu_kb.get_keyboard())
				case 'add_telegram_bot':
					message_id = int(data[1])
					telegram_bot_name: str = data[2]

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					if telegram_bot_name == 'None':
						self.wait_user_message.update({user_id: f'add_telegram_bot:{message_id}:{message}'})

						context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Введите Token Telegram бота:', reply_markup=self.cancel_comand_kb.get_keyboard())
					else:
						del self.wait_user_message[user_id]

						result = GlobalFunctions.add_telegram_bot(self.db, self.config, telegram_bot_name, message)
						context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_admin_menu_kb.get_keyboard())
				case 'add_superuser':
					message_id = int(data[1])

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					del self.wait_user_message[user_id]

					result = GlobalFunctions.add_superuser(self.db, message)
					context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_admin_menu_kb.get_keyboard())

	@check_user
	@get_user_data(arugments_list=['context', 'chat_id'])
	def start_command(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int) -> None: # Метод для команды /start
		context.bot.send_message(chat_id=chat_id, text='🔐 <b>Админ меню</b> 🔐', parse_mode='HTML', reply_markup=self.admin_menu_kb.get_keyboard())
	
	@get_user_data(arugments_list=['context', 'chat_id', 'message_id'])
	def telegram_bots(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 1
		message, num = '<b>Список ваших Telegram ботов:</b>', 1
		for telegram_bot in self.db.get_data(table='TelegramBots', fetchall=True):
			message += f'\n{num}. {telegram_bot[1]}'
			num += 1
		
		telegram_bots_kb = Keyboard(inline=True)
		telegram_bots_kb.add_button([{'text': 'Настройки Telegram бота', 'callback_data': 'telegram_bot_settings'}])
		telegram_bots_kb.add_button([{'text': 'Список пользователей Telegram бота', 'callback_data': 'telegram_bot_users'}])
		telegram_bots_kb.add_button([{'text': 'Добавить Telegram бота', 'callback_data': 'add_telegram_bot'}])
		telegram_bots_kb.add_button([{'text': 'Удалить Telegram бота', 'callback_data': 'delete_telegram_bot'}])
		telegram_bots_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bots_kb.get_keyboard())

	def select_telegram_bot(func) -> None: # Декоратор для получения ID бота, который выберет пользователь
		def wrapper(*args, **kwargs):
			callback_data: str = kwargs['callback_data']
			if callback_data.find(':') == -1:
				self, context, chat_id, message_id = kwargs['self'], kwargs['context'], kwargs['chat_id'], kwargs['message_id']

				buttons, message, num = [], '<b>Выберите Telegram бота:</b>', 1
				for telegram_bot in self.db.get_data(table='TelegramBots', fetchall=True):
					message += f'\n{num}. {telegram_bot[1]}'
					buttons.append({'text': str(num), 'callback_data': f'{func.__name__}:{telegram_bot[0]}'})
					num += 1

				select_telegram_bot_kb = Keyboard(inline=True)
				select_telegram_bot_kb.add_button(buttons)
				select_telegram_bot_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
				context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=select_telegram_bot_kb.get_keyboard())
			else:
				del kwargs['callback_data']
				kwargs.update({'telegram_bot_id': int(callback_data.split(':')[1])})
				func(*args, **kwargs)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_settings(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		message = f'<b>Настройки {telegram_bot_name.capitalize()} Telegram бота:</b>'
		message += f"\n1. Тип {telegram_bot_name.capitalize()} Telegram бота: <i>{'Приватный' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else 'Не приватный'}</i>"
		message += f"\n2. Токен {telegram_bot_name.capitalize()} Telegram бота: <i>{self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Token']}</i>"

		telegram_bot_settings_kb = Keyboard(inline=True)
		telegram_bot_settings_kb.add_button([{'text': 'Изменить тип Telegram бота', 'callback_data': f'edit_telegram_bot_type:{telegram_bot_id}'}])
		telegram_bot_settings_kb.add_button([{'text': 'Изменить токен Telegram бота', 'callback_data': f'edit_telegram_bot_token:{telegram_bot_id}'}])
		telegram_bot_settings_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_settings_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_type(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1:1
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] = '0' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else '1'
		with open('./data/config.ini', 'w') as config_file:
			self.config.write(config_file)
		self.config.read('data/config.ini')

		edit_telegram_bot_type_kb = Keyboard(inline=True)
		edit_telegram_bot_type_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_settings:{telegram_bot_id}'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Теперь {telegram_bot_name.capitalize()} Telegram бот {'приватный' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else 'не приватный'}.", parse_mode='HTML', reply_markup=edit_telegram_bot_type_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_token(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]
		
		self.wait_user_message.update({user_id: f'edit_telegram_bot_token:{message_id}:{telegram_bot_id}'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Введите новый токен {telegram_bot_name.capitalize()} Telegram бота:', reply_markup=self.cancel_comand_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_users(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]
		users: list = self.db.get_data(table=f'{telegram_bot_name.capitalize()}TelegramBotUsers', fetchall=True)

		message, num = f'<b>Список пользователей {telegram_bot_name.capitalize()} Telegram бота:</b>', 1
		for user in users:
			message += f"""\n{num}. Пользователь: {user[2]} | ID пользователя: {user[0]} | ID чата: {user[1]} | Дата активации бота: {user[3]} | Пользователь {'не' if user[4] == 0 and self.config['AdminTelegramBot']['Private'] == '1' and self.db.get_data(table='Superusers', where=f"username='{user[2]}'", fetchone=True) == None else ''} имеет доступ к боту."""

		if message == f'<b>Список пользователей {telegram_bot_name.capitalize()} Telegram бота:</b>':
			message = f'<b>Вашего {telegram_bot_name.capitalize()} Telegram бота ещё никто не активировал!</b>'

		telegram_bot_users_kb = Keyboard(inline=True)
		telegram_bot_users_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_users_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id'])
	def add_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int) -> None: # Метод для кнопки 1:3
		self.wait_user_message.update({user_id: f'add_telegram_bot:{message_id}:None'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Придумайте имя Telegram боту:', reply_markup=self.cancel_comand_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def delete_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:4
		result = GlobalFunctions.delete_telegram_bot(self.db, self.config, telegram_bot_id)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_admin_menu_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id'])
	def superusers(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 2
		message, num = '<b>Список суперпользователей:</b>', 1
		for superuser in self.db.get_data(table='Superusers', fetchall=True):
			message += f'\n{num}. {superuser[1]}'
			num += 1

		superusers_kb = Keyboard(inline=True)
		superusers_kb.add_button([{'text': 'Добавить суперпользователя', 'callback_data': 'add_superuser'}])		
		if message == '<b>Список суперпользователей:</b>':
			message = '<b>У вас нет ещё суперпользователей!</b>'
		else:
			superusers_kb.add_button([{'text': 'Удалить суперпользователя', 'callback_data': 'delete_superuser'}])
		superusers_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=superusers_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id'])
	def add_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int) -> None: # Метод для кнопки 2:1
		self.wait_user_message.update({user_id: f'add_superuser:{message_id}'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Введите @ пользователя:', reply_markup=self.cancel_comand_kb.get_keyboard())

	def select_superuser(func) -> None: # Декоратор для получения ID суперпользователя, который выберет пользователь
		def wrapper(*args, **kwargs):
			callback_data: str = kwargs['callback_data']
			if callback_data.find(':') == -1:
				self, context, chat_id, message_id = kwargs['self'], kwargs['context'], kwargs['chat_id'], kwargs['message_id']

				buttons, message, num = [], '<b>Список суперпользователей:</b>', 1
				for superuser in self.db.get_data(table='Superusers', fetchall=True):
					message += f'\n{num}. {superuser[1]}'
					buttons.append({'text': str(num), 'callback_data': f'{func.__name__}:{superuser[0]}'})
					num += 1

				select_telegram_bot_kb = Keyboard(inline=True)
				select_telegram_bot_kb.add_button(buttons)
				select_telegram_bot_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
				context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=select_telegram_bot_kb.get_keyboard())
			else:
				del kwargs['callback_data']
				kwargs.update({'superuser_id': int(callback_data.split(':')[1])})
				func(*args, **kwargs)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_superuser
	def delete_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, superuser_id: int) -> None: # Метод для кнопки 2:2
		result = GlobalFunctions.delete_superuser(db=self.db, superuser_id=superuser_id)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_admin_menu_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id'])
	def back_to_admin_menu(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 0
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='🔐 <b>Админ меню</b> 🔐', parse_mode='HTML', reply_markup=self.admin_menu_kb.get_keyboard())

	@get_user_data(arugments_list=['update', 'context', 'user_id'])
	def cancel_comand(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, user_id: int) -> None: # Метод для кнопки -1
		if user_id in self.wait_user_message:
			del self.wait_user_message[user_id]
		self.back_to_admin_menu(update, context)

	def start(self) -> None: # Метод для запуска Telegram бота
		self.updater = Updater(token=self.config['AdminTelegramBot']['Token'])
		self.dispatcher = self.updater.dispatcher

		self.dispatcher.add_handler(CallbackQueryHandler(self.handle_callback_query))

		new_message_handler = MessageHandler(Filters.text & (~Filters.command), self.new_message)
		self.dispatcher.add_handler(new_message_handler)

		for command in self.commands:
			handler = CommandHandler(command, self.commands[command])
			self.dispatcher.add_handler(handler)

		self.updater.start_polling()

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')