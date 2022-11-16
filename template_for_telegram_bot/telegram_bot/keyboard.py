from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class Keyboard:
	def __init__(self, inline: bool):
		self.inline = inline

		if self.inline:
			self.kb = InlineKeyboardMarkup()
		else:
			self.kb = ReplyKeyboardMarkup()
	
	def add_button(self, buttons: list):
		"""
		### InlineKeyboardMarkup
		buttons = [{'text': 'Привет'}, {'text': 'Пока'}]

		### ReplyKeyboardMarkup
		buttons = [{'text': 'Привет', 'callback_data': 'Hello'}, {'text': 'Пока', 'callback_data': 'Bye'}]
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

	def get_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
		return dict(self.kb)

if __name__ == '__main__':
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')