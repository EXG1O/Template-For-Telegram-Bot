# Для работы Telegram бота
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram.ext
import telegram

# Для работы с клавиатурой и базой данных Telegram бота
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
			# 'add_telegram_bot': self.add_telegram_bot, # 1:3
			# 'delete_telegram_bot': self.delete_telegram_bot, # 1:4
			'superusers': self.superusers, # 2
			# 'add_superuser': self.add_superuser, # 2:1
			# 'delete_superuser': self.delete_superuser, # 2:2
			'back_to_admin_menu': self.back_to_admin_menu # 0
		}

		self.admin_menu_kb = Keyboard(inline=True)
		self.admin_menu_kb.add_button([{'text': 'Список ваших Telegram ботов', 'callback_data': 'telegram_bots'}])
		self.admin_menu_kb.add_button([{'text': 'Суперпользователи', 'callback_data': 'superusers'}])

	def check_user(func) -> None: # Декоратор для проверки доступа пользователя к данному боту
		def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
			chat_id, user_id, username = update.effective_chat.id, update.effective_user.id, update.effective_user.name

			if self.db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True) == None:
				user = self.db.get_data(table='AdminTelegramBotUsers', where=f"user_id='{user_id}'", fetchone=True)
				if user != None:
					if user[4] == 1:
						func(self, update, context)
					else:
						context.bot.send_message(chat_id=chat_id, text='Вы не имете доступ к данному боту!')
				else:
					values = (
						user_id,
						chat_id,
						username,
						str(datetime.now()).split('.')[0],
						0 if self.config['AdminTelegramBot']['Private'] == '1' else 1
					)
					self.db.insert_into(table='AdminTelegramBotUsers', values=values)

					if self.config['AdminTelegramBot']['Private'] == '1':
						context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, ожидайте пока вам разрешат им пользоваться.')
					else:
						context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, и можете пользоваться ботом.')
			else:
				func(self, update, context)
		wrapper.__name__ = func.__name__
		return wrapper

	def get_user_data(data_list: list) -> None: # Декоратор для получения необходимой информации
		def decorator(func):
			def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
				data_dict = {'self': self}
				for data in data_list:
					match data:
						case 'update':
							data_dict.update({'update': update})
						case 'context':
							data_dict.update({'context': context})
						case 'chat_id':
							data_dict.update({'chat_id': update.effective_chat.id})
						case 'user_id':
							data_dict.update({'user_id': update.effective_user.id})
						case 'username':
							data_dict.update({'username': update.effective_user.username})
						case 'message_id':
							data_dict.update({'message_id': update.effective_message.message_id})
						case 'callback_data':
							data_dict.update({'callback_data': update.callback_query.data})
				func(**data_dict)
			wrapper.__name__ = func.__name__
			return wrapper
		return decorator

	@check_user
	def handle_callback_query(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext) -> None: # Метод для обработки Callback
		data = update.callback_query.data.split(':')[0]
		if data in self.callback:
			self.callback[data](update, context)
	
	@check_user
	@get_user_data(data_list=['update', 'context', 'user_id', 'chat_id'])
	def new_message(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int) -> None: # Метод для обработки сообщений
		message = update.effective_message.text
		
		if user_id in self.wait_user_message:
			match self.wait_user_message[user_id].split(':')[0]:
				case 'edit_telegram_bot_token':
					message_id = int(self.wait_user_message[user_id].split(':')[2])
					telegram_bot_id = self.wait_user_message[user_id].split(':')[1]
					telegram_bot_name = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

					self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Token'] = message
					with open('./data/config.ini', 'w') as config_file:
						self.config.write(config_file)
					self.config.read('data/config.ini')

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					del self.wait_user_message[user_id]

					edit_telegram_bot_type_kb = Keyboard(inline=True)
					edit_telegram_bot_type_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_settings:{telegram_bot_id}'}])
					context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Теперь токен Telegram бота {telegram_bot_name.capitalize()}: <i>{message}</i>\n<b>Чтобы изменения вступили в силу, перезапустите файл main.py!</b>', parse_mode='HTML', reply_markup=edit_telegram_bot_type_kb.get_keyboard())

	@check_user
	@get_user_data(data_list=['context', 'chat_id'])
	def start_command(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int) -> None: # Метод для команды /start
		context.bot.send_message(chat_id=chat_id, text='🔐 <b>Админ меню</b> 🔐', parse_mode='HTML', reply_markup=self.admin_menu_kb.get_keyboard())
	
	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
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
			callback_data = kwargs['callback_data']
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

	@get_user_data(data_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_settings(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1
		telegram_bot_name = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		message = '<b>Настройки Telegram бота:</b>'
		message += f"\n1. Тип Telegram бота: <i>{'Приватный' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else 'Не приватный'}</i>"
		message += f"\n2. Токен Telegram бота: <i>{self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Token']}</i>"

		telegram_bot_settings_kb = Keyboard(inline=True)
		telegram_bot_settings_kb.add_button([{'text': 'Изменить тип Telegram бота', 'callback_data': f'edit_telegram_bot_type:{telegram_bot_id}'}])
		telegram_bot_settings_kb.add_button([{'text': 'Изменить токен Telegram бота', 'callback_data': f'edit_telegram_bot_token:{telegram_bot_id}'}])
		telegram_bot_settings_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_settings_kb.get_keyboard())

	@get_user_data(data_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_type(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1:1
		telegram_bot_name = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] = '0' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else '1'
		with open('./data/config.ini', 'w') as config_file:
			self.config.write(config_file)
		self.config.read('data/config.ini')

		edit_telegram_bot_type_kb = Keyboard(inline=True)
		edit_telegram_bot_type_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_settings:{telegram_bot_id}'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Теперь Telegram бот {telegram_bot_name.capitalize()} {'приватный' if self.config[f'{telegram_bot_name.capitalize()}TelegramBot']['Private'] == '1' else 'не приватный'}.", parse_mode='HTML', reply_markup=edit_telegram_bot_type_kb.get_keyboard())

	@get_user_data(data_list=['context', 'user_id', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_token(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1:2
		self.wait_user_message.update({user_id: f'edit_telegram_bot_token:{telegram_bot_id}:{message_id}'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Введите новый токен Telegram бота:', parse_mode='HTML')

	@get_user_data(data_list=['context', 'user_id', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_users(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]
		users = self.db.get_data(table=f'{telegram_bot_name.capitalize()}TelegramBotUsers', fetchall=True)

		message, num = f'<b>Список пользователей Telegram бота {telegram_bot_name.capitalize()}</b>', 1
		for user in users:
			message += f"\n{num}. Пользователь: {user[2]} | ID пользователя: {user[0]} | ID чата: {user[1]} | Дата активации бота: {user[3]} | Пользователь {'не' if user[4] == 0 else ''} имеет доступ к боту."

		telegram_bot_users_kb = Keyboard(inline=True)
		telegram_bot_users_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_users_kb.get_keyboard())

	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def add_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 1:3
		pass

	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def delete_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 1:4
		pass

	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def add_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 2:1
		pass
	
	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def delete_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 2:2
		pass

	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def superusers(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 2
		message, num = '<b>Список суперпользователей</b>', 1
		for superuser in self.db.get_data(table='Superusers', fetchall=True):
			message = f'\n{num}. {superuser[1]}'
			num += 1

		superusers_kb = Keyboard(inline=True)
		superusers_kb.add_button([{'text': 'Добавить суперпользователя', 'callback_data': 'add_superuser'}])
		superusers_kb.add_button([{'text': 'Удалить суперпользователя', 'callback_data': 'delete_superuser'}])
		superusers_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=superusers_kb.get_keyboard())

	@get_user_data(data_list=['context', 'chat_id', 'message_id'])
	def back_to_admin_menu(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 0
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='🔐 <b>Админ меню</b> 🔐', parse_mode='HTML', reply_markup=self.admin_menu_kb.get_keyboard())

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