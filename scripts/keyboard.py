from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Класс Keyboard
class Keyboard:
	def __init__(self, inline: bool): # Инициализация класса Keyboard
		self.inline = inline

		if self.inline:
			self.kb = InlineKeyboardMarkup(row_width=4)
		else:
			self.kb = ReplyKeyboardMarkup(row_width=4)
	
	def add_button(self, buttons: list): # Метод добавление кнопок в клавиатуру Telegram бота
		"""
		### InlineKeyboardMarkup
		buttons = [{'text': 'Привет'}, {'text': 'Пока'}]

		### ReplyKeyboardMarkup
		buttons = [{'text': 'Привет', 'callback_data': 'hello'}, {'text': 'Пока', 'callback_data': 'bye'}]
		"""

		if type(buttons) == list:
			if buttons != []:
				buttons_ = []
				for button in buttons:
					if self.inline:
						buttons_.append(InlineKeyboardButton(text=button['text'], callback_data=button['callback_data']))
					else:
						buttons_.append(KeyboardButton(text=button['text']))

				self.kb.add(*buttons_)
			else:
				raise Exception('Аргумент "buttons" пустой!')
		else:
			raise Exception('Аргумент "buttons" не является массивом!')

	def get_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:  # Метод для получения клавиатуры Telegram бота
		return dict(self.kb)

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')