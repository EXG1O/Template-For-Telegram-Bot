from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram.ext
import telegram

from telegram_bot.keyboard import Keyboard

from configparser import ConfigParser
import logging

class AdminTelegramBot:
	def __init__(self, config: ConfigParser):
		self.config = config

		self.commands = {
			'start': self.start_command
		}

		self.updater = Updater(token=self.config['AdminTelegramBot']['Token'])
		self.dispatcher = self.updater.dispatcher

	def get_user_data(func):
		def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
			chat_id, user_id, username = update.effective_chat.id, update.effective_user.id, update.effective_user.name

			func(self, update, context, chat_id, user_id, username)
		wrapper.__name__ = func.__name__
		return wrapper

	@get_user_data
	def handle_callback_query(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, user_id: int, username: str):
		data = update.callback_query.data
		print(f'{chat_id} - {username} - {data}')
	
	@get_user_data
	def new_message(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, user_id: int, username: str):
		message = update.effective_message.text
		print(f'{chat_id} - {username} - {message}')

	@get_user_data
	def start_command(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext, chat_id: int, user_id: int, username: str):
		context.bot.send_message(chat_id=chat_id, text='Start command!')

	def start(self):
		self.dispatcher.add_handler(CallbackQueryHandler(self.handle_callback_query))

		new_message_handler = MessageHandler(Filters.text, self.new_message)
		self.dispatcher.add_handler(new_message_handler)

		for command in self.commands:
			handler = CommandHandler(command, self.commands[command])
			self.dispatcher.add_handler(handler)

		self.updater.start_polling()

if __name__ == '__main__':
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')