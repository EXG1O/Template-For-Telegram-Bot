from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram.ext
import telegram

from scripts.custom_configparser import CustomConfigParser
from scripts.decorators import check_user, get_user_data
from scripts.keyboard import Keyboard
from scripts.database import DataBase

from configparser import ConfigParser

# Класс TemplateTelegramBot
class TemplateTelegramBot:
	def __init__(self, telegram_bot_name: str) -> None: # Инициализация класса TemplateTelegramBot
		self.config = CustomConfigParser().config
		self.db = DataBase()

		self.telegram_bot_name = telegram_bot_name
		self.commands = {
			'start': self.start_command
		}

	@check_user
	@get_user_data(arugments_list=['update', 'user_id', 'username'])
	def handle_callback_query(self, update: telegram.update.Update, user_id: int, username: str): # Метод для обработки Callback
		data = update.callback_query.data
		print(f'{user_id} - {username} - {data}')
	
	@check_user
	@get_user_data(arugments_list=['update', 'user_id', 'username'])
	def new_message(self, update: telegram.update.Update, user_id: int, username: str): # Метод для обработки сообщений
		message = update.effective_message.text
		print(f'{user_id} - {username} - {message}')

	@check_user
	@get_user_data(arugments_list=['context', 'chat_id'])
	def start_command(self, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int): # Метод для команды /start
		context.bot.send_message(chat_id=chat_id, text='Start command!')

	def start(self): # Метод для запуска Telegram бота
		self.updater = Updater(token=self.config['TemplateTelegramBot']['Token'])
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