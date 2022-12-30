from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram.ext
import telegram

from scripts.decorators import check_user, get_user_data
import scripts.functions as GlobalFunctions
from scripts.variables import Variables
from scripts.keyboard import Keyboard
from scripts.database import DataBase

# Класс AdminTelegramBot
class AdminTelegramBot:
	def __init__(self, telegram_bot_name: str) -> None: # Инициализация класса AdminTelegramBot
		self.config = Variables().config
		self.db = DataBase()

		self.telegram_bot_name = telegram_bot_name
		self.wait_user_message = {}
		self.commands = {
			'start': self.start_command
		}
		self.callback = {
			'telegram_bots': self.telegram_bots, # 1
			'start_telegram_bot': self.start_telegram_bot, # 1:1
			'stop_telegram_bot': self.stop_telegram_bot, # 1:2
			'telegram_bot_settings': self.telegram_bot_settings, # 1:3
			'edit_telegram_bot_type': self.edit_telegram_bot_type, # 1:3:1
			'edit_telegram_bot_token': self.edit_telegram_bot_token, # 1:3:2
			'telegram_bot_users': self.telegram_bot_users, # 1:4
			'give_access_user': self.give_access_user, # 1:4:1
			'make_superuser': self.make_superuser, # 1:4:2
			'delete_user': self.delete_user, # 1:4:3
			'add_telegram_bot': self.add_telegram_bot, # 1:5
			'delete_telegram_bot': self.delete_telegram_bot, # 1:6
			'superusers': self.superusers, # 2
			'add_superuser': self.add_superuser, # 2:1
			'delete_superuser': self.delete_superuser, # 2:2
			'back_to_admin_menu': self.back_to_admin_menu, # 0
			'cancel_comand': self.cancel_comand # -1
		}

		self.admin_menu_kb = Keyboard(inline=True)
		self.admin_menu_kb.add_button(
			[
				{
					'text': 'Список Telegram ботов',
					'callback_data': 'telegram_bots'
				},
				{
					'text': 'Суперпользователи',
					'callback_data': 'superusers'
				}
			]
		)

		self.back_to_telegram_bots_kb = Keyboard(inline=True)
		self.back_to_telegram_bots_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])

		self.back_to_superusers_kb = Keyboard(inline=True)
		self.back_to_superusers_kb.add_button([{'text': 'Вернуться', 'callback_data': 'superusers'}])

		self.cancel_comand_kb = Keyboard(inline=True)
		self.cancel_comand_kb.add_button([{'text': 'Отменить', 'callback_data': 'cancel_comand'}])

	@check_user
	def handle_callback_query(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext) -> None: # Метод для обработки Callback
		callback_data: str = update.callback_query.data.split(':')[0]
		if callback_data in self.callback:
			self.callback[callback_data](update, context)
	
	@check_user
	@get_user_data(arugments_list=['update', 'context', 'user_id', 'chat_id'])
	def new_message(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int) -> None: # Метод для обработки сообщений
		message: str = update.effective_message.text
		
		if user_id in self.wait_user_message:
			data: list = self.wait_user_message[user_id].split(':')
			message_id: int = int(data[1])

			match data[0]:
				case 'edit_telegram_bot_token':
					telegram_bot_id: int = int(data[2])
					telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1].capitalize()

					self.config[f'{telegram_bot_name}TelegramBot']['Token'] = message
					with open('./data/config.ini', 'w') as config_file:
						self.config.write(config_file)
					self.config.read('data/config.ini')

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					del self.wait_user_message[user_id]

					edit_telegram_bot_token_kb = Keyboard(inline=True)
					edit_telegram_bot_token_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_settings:{telegram_bot_id}'}])
					context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Теперь токен {telegram_bot_name} Telegram бота: <i>{message}</i>\n<b>Чтобы изменения вступили в силу, перезапустите файл main.py!</b>', parse_mode='HTML', reply_markup=edit_telegram_bot_token_kb.get_keyboard())
				case 'add_telegram_bot':
					telegram_bot_name: str = data[2].lower()

					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					if telegram_bot_name == 'None':
						self.wait_user_message.update({user_id: f'add_telegram_bot:{message_id}:{message}'})

						context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Введите Token Telegram бота:', reply_markup=self.cancel_comand_kb.get_keyboard())
					else:
						del self.wait_user_message[user_id]

						result: str = GlobalFunctions.add_telegram_bot(telegram_bot_name=telegram_bot_name, telegram_bot_token=message)
						self.config.read('data/config.ini')

						context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_telegram_bots_kb.get_keyboard())
				case 'add_superuser':
					context.bot.delete_message(chat_id=chat_id, message_id=update.effective_message.message_id)
					del self.wait_user_message[user_id]

					result: str = GlobalFunctions.add_superuser(username=message)
					context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_superusers_kb.get_keyboard())

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
		telegram_bots_kb.add_button(
			[
				{
					'text': 'Запустить Telegram бота',
					'callback_data': 'start_telegram_bot'
				},
				{
					'text': 'Остановить Telegram бота',
					'callback_data': 'stop_telegram_bot'
				},
				{
					'text': 'Настройки Telegram бота',
					'callback_data': 'telegram_bot_settings'
				},
				{
					'text': 'Список пользователей Telegram бота',
					'callback_data': 'telegram_bot_users'
				},
				{
					'text': 'Добавить Telegram бота',
					'callback_data': 'add_telegram_bot'
				},
				{
					'text': 'Удалить Telegram бота',
					'callback_data': 'delete_telegram_bot'
				},
				{
					'text': 'Вернуться',
					'callback_data': 'back_to_admin_menu'
				}
			]
		)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bots_kb.get_keyboard())

	def select_telegram_bot(func) -> None: # Декоратор для получения ID Telegram бота, который выберет пользователь
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
				select_telegram_bot_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])
				context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=select_telegram_bot_kb.get_keyboard())
			else:
				del kwargs['callback_data']
				kwargs.update({'telegram_bot_id': int(callback_data.split(':')[1])})
				func(*args, **kwargs)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def start_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:1
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		telegram_bots: dict = Variables().telegram_bots 
		if telegram_bot_name not in telegram_bots:
			result: str = GlobalFunctions.start_telegram_bot(telegram_bot_name=telegram_bot_name)
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, parse_mode='HTML', reply_markup=self.back_to_telegram_bots_kb.get_keyboard())
		else:
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'{telegram_bot_name.capitalize()} Telegram бот уже запущен!', parse_mode='HTML', reply_markup=self.back_to_telegram_bots_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def stop_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1]

		telegram_bots = Variables().telegram_bots 
		if telegram_bot_name in telegram_bots:
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'{telegram_bot_name.capitalize()} Telegram бот успешно остановлен.', parse_mode='HTML', reply_markup=self.back_to_telegram_bots_kb.get_keyboard())

			telegram_bot = telegram_bots[telegram_bot_name]
			del telegram_bots[telegram_bot_name]
			telegram_bot.stop()
		else:
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'{telegram_bot_name.capitalize()} Telegram бот уже остановлен!', parse_mode='HTML', reply_markup=self.back_to_telegram_bots_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_settings(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:3
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1].capitalize()

		message = f"""\
			<b>Тип:</b> <i>{'Приватный' if self.config[f'{telegram_bot_name}TelegramBot']['Private'] == '1' else 'Не приватный'}</i>
			<b>Токен:</b> <i>{self.config[f'{telegram_bot_name}TelegramBot']['Token']}</i>
		""".replace('	', '')

		telegram_bot_settings_kb = Keyboard(inline=True)
		telegram_bot_settings_kb.add_button(
			[
				{
					'text': 'Изменить тип Telegram бота',
					'callback_data': f'edit_telegram_bot_type:{telegram_bot_id}'
				},
				{
					'text': 'Изменить токен Telegram бота',
					'callback_data': f'edit_telegram_bot_token:{telegram_bot_id}'
				},
				{
					'text': 'Вернуться',
					'callback_data': 'telegram_bots'
				}
			]
		)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_settings_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_type(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:3:1
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1].capitalize()

		self.config[f'{telegram_bot_name}TelegramBot']['Private'] = '0' if self.config[f'{telegram_bot_name}TelegramBot']['Private'] == '1' else '1'
		with open('./data/config.ini', 'w') as config_file:
			self.config.write(config_file)
		self.config.read('data/config.ini')

		edit_telegram_bot_type_kb = Keyboard(inline=True)
		edit_telegram_bot_type_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_settings:{telegram_bot_id}'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Теперь {telegram_bot_name} Telegram бот {'приватный' if self.config[f'{telegram_bot_name}TelegramBot']['Private'] == '1' else 'не приватный'}.", parse_mode='HTML', reply_markup=edit_telegram_bot_type_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def edit_telegram_bot_token(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:3:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1].capitalize()
		
		self.wait_user_message.update({user_id: f'edit_telegram_bot_token:{message_id}:{telegram_bot_id}'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Введите новый токен {telegram_bot_name} Telegram бота:', reply_markup=self.cancel_comand_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def telegram_bot_users(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:4
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f"id='{telegram_bot_id}'", fetchone=True)[1].capitalize()
		users: list = self.db.get_data(table=f'{telegram_bot_name}TelegramBotUsers', fetchall=True)

		message = ''
		for user in users:
			message += f"""
				<b>Пользователь {user[2]}</b>
				ID пользователя: {user[0]}
				ID чата: {user[1]}
				Дата активации бота: {user[3]}
				Пользователь {'не' if user[4] == 0 and self.config['AdminTelegramBot']['Private'] == '1' and self.db.get_data(table='Superusers', where=f"username='{user[2]}'", fetchone=True) == None else ''}имеет доступ к боту.
			""".replace('	', '')

		telegram_bot_users_kb = Keyboard(inline=True)
		if message == '':
			message = f'<b>Вашего {telegram_bot_name} Telegram бота ещё никто не активировал!</b>'
		else:
			telegram_bot_users_kb.add_button(
				[
					{
						'text': 'Выдать доступ к боту',
						'callback_data': f'give_access_user:{telegram_bot_id}:None'
					},
					{
						'text': 'Сделать суперпользователем',
						'callback_data': f'make_superuser:{telegram_bot_id}:None'
					},
					{
						'text': 'Удалить пользователя',
						'callback_data': f'delete_user:{telegram_bot_id}:None'
					}
				]
			)
		telegram_bot_users_kb.add_button([{'text': 'Вернуться', 'callback_data': 'telegram_bots'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=telegram_bot_users_kb.get_keyboard())

	def select_telegram_bot_user(func) -> None: # Декоратор для получения ID пользователя Telegram бота, который выберет пользователь
		def wrapper(*args, **kwargs):
			callback_data: str = kwargs['callback_data']
			callback_data_elements: list = callback_data.split(':')
			telegram_bot_id: int = int(callback_data_elements[1])

			if callback_data_elements[2] == 'None':
				self, context, chat_id, message_id = kwargs['self'], kwargs['context'], kwargs['chat_id'], kwargs['message_id']
				telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f'id={telegram_bot_id}', fetchone=True)[1].capitalize()

				buttons, message, num = [], f'<b>Выберите пользователя {telegram_bot_name} Telegram бота:</b>', 1
				for user in self.db.get_data(table=f'{telegram_bot_name}TelegramBotUsers', fetchall=True):
					message += f'\n{num}. {user[2]}'
					buttons.append({'text': str(num), 'callback_data': f'{func.__name__}:{telegram_bot_id}:{user[0]}'})
					num += 1

				select_telegram_bot_user_kb = Keyboard(inline=True)
				select_telegram_bot_user_kb.add_button(buttons)
				select_telegram_bot_user_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_users:{telegram_bot_id}'}])
				context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=select_telegram_bot_user_kb.get_keyboard())
			else:
				del kwargs['callback_data']
				kwargs.update(
					{
						'telegram_bot_id': telegram_bot_id,
						'telegram_bot_user_id': int(callback_data_elements[2])
					}
				)
				func(*args, **kwargs)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot_user
	def give_access_user(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int, telegram_bot_user_id: int) -> None: # Метод для кнопки 1:4:1
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f'id={telegram_bot_id}', fetchone=True)[1].capitalize()
		user: tuple = self.db.get_data(table=f'{telegram_bot_name}TelegramBotUsers', where=f'user_id={telegram_bot_user_id}', fetchone=True)

		give_access_user_kb = Keyboard(inline=True)
		give_access_user_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_users:{telegram_bot_id}'}])

		if user[4] == 0 and self.db.get_data(table='Superusers', where=f"username='{user[2]}'", fetchone=True) == None:
			self.db.edit_value(table=f'{telegram_bot_name}TelegramBotUsers', value='allowed_user=1', where=f'user_id={telegram_bot_user_id}')
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Вы успешно выдали доступ пользователю {user[2]} к {telegram_bot_name} Telegram боту.', parse_mode='HTML', reply_markup=give_access_user_kb.get_keyboard())
		else:
			context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Пользователь {user[2]} уже имеет доступ к {telegram_bot_name} Telegram боту!', parse_mode='HTML', reply_markup=give_access_user_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot_user
	def make_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int, telegram_bot_user_id: int) -> None: # Метод для кнопки 1:4:2
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f'id={telegram_bot_id}', fetchone=True)[1].capitalize()
		username: str = self.db.get_data(table=f'{telegram_bot_name}TelegramBotUsers', where=f'user_id={telegram_bot_user_id}', fetchone=True)[2]

		result: str = GlobalFunctions.add_superuser(username=username)

		make_superuser_kb = Keyboard(inline=True)
		make_superuser_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_users:{telegram_bot_id}'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, parse_mode='HTML', reply_markup=make_superuser_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot_user
	def delete_user(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int, telegram_bot_user_id: int) -> None: # Метод для кнопки 1:4:3
		telegram_bot_name: str = self.db.get_data(table='TelegramBots', where=f'id={telegram_bot_id}', fetchone=True)[1].capitalize()
		username: str = self.db.get_data(table=f'{telegram_bot_name}TelegramBotUsers', where=f'user_id={telegram_bot_user_id}', fetchone=True)[2]

		self.db.delete_record(table=f'{telegram_bot_name}TelegramBotUsers', where=f'user_id={telegram_bot_user_id}')

		delete_user_kb = Keyboard(inline=True)
		delete_user_kb.add_button([{'text': 'Вернуться', 'callback_data': f'telegram_bot_users:{telegram_bot_id}'}])
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Вы успешно удалили пользователя {username} из {telegram_bot_name} Telegram бота.', parse_mode='HTML', reply_markup=delete_user_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id'])
	def add_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int) -> None: # Метод для кнопки 1:5
		self.wait_user_message.update({user_id: f'add_telegram_bot:{message_id}:None'})
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Придумайте имя Telegram боту:', reply_markup=self.cancel_comand_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_telegram_bot
	def delete_telegram_bot(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, telegram_bot_id: int) -> None: # Метод для кнопки 1:6
		result: str = GlobalFunctions.delete_telegram_bot(telegram_bot_id=telegram_bot_id)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_telegram_bots_kb.get_keyboard())

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

				select_superuser_kb = Keyboard(inline=True)
				select_superuser_kb.add_button(buttons)
				select_superuser_kb.add_button([{'text': 'Вернуться', 'callback_data': 'back_to_admin_menu'}])
				context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message, parse_mode='HTML', reply_markup=select_superuser_kb.get_keyboard())
			else:
				del kwargs['callback_data']
				kwargs.update({'superuser_id': int(callback_data.split(':')[1])})
				func(*args, **kwargs)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id', 'callback_data'])
	@select_superuser
	def delete_superuser(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int, superuser_id: int) -> None: # Метод для кнопки 2:2
		result: str = GlobalFunctions.delete_superuser(superuser_id=superuser_id)
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=result, reply_markup=self.back_to_superusers_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'chat_id', 'message_id'])
	def back_to_admin_menu(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, message_id: int) -> None: # Метод для кнопки 0
		context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='🔐 <b>Админ меню</b> 🔐', parse_mode='HTML', reply_markup=self.admin_menu_kb.get_keyboard())

	@get_user_data(arugments_list=['context', 'user_id', 'chat_id', 'message_id'])
	def cancel_comand(self, context: telegram.ext.callbackcontext.CallbackContext, user_id: int, chat_id: int, message_id: int) -> None: # Метод для кнопки -1
		if user_id in self.wait_user_message:
			del self.wait_user_message[user_id]
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

	def stop(self) -> None: # Метод для остановки Telegram бота
		self.updater.stop()

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')