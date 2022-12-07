# Для работы с DataBase.db
from configparser import ConfigParser
from threading import Lock
import sqlite3

# Класс DataBase
class DataBase:
	def __init__(self, config: ConfigParser, lock: Lock) -> None: # Инициализация класса DataBase
		self.lock = lock

		self.db = sqlite3.connect('./data/DataBase.db', check_same_thread=False)
		self.sql = self.db.cursor()

	def lock_and_unlock_theards(func): # Декоратор для Lock/Unlock всех потоков в программе
		def wrapper(*args, **kwargs):
			self = args[0]

			self.lock.acquire()
			data = func(*args, **kwargs)
			self.lock.release()

			return data
		wrapper.__name__ = func.__name__
		return wrapper

	@lock_and_unlock_theards
	def create_table(self, table: str, values: str) -> None: # Метод для создания таблиц в базе данных
		self.sql.execute(f"CREATE TABLE IF NOT EXISTS {table} ({values})")
		self.db.commit()
	
	@lock_and_unlock_theards
	def drop_table(self, table: str) -> None: # Метод для удаления таблиц из базы данных
		self.sql.execute(f"DROP TABLE IF EXISTS {table}")
		self.db.commit()

	@lock_and_unlock_theards
	def insert_into(self, table: str, values: tuple) -> None: # Метод для записи данных в таблицу баз данных
		question_marks = ''
		for num in range(len(values)):
			question_marks += '?, '
		question_marks = ', '.join(question_marks.split(', ')[0:-1])

		self.sql.execute(f"INSERT INTO {table} VALUES ({question_marks})", values)
		self.db.commit()

	@lock_and_unlock_theards
	def delete_record(self, table: str, where: str | None = None) -> None: # Метод для удаления записей из таблицы базы данных
		if where == None:
			self.sql.execute(f"DELETE FROM {table}")
		else:
			self.sql.execute(f"DELETE FROM {table} WHERE {where}")
		self.db.commit()

	@lock_and_unlock_theards
	def edit_value(self, table: str, value: str, where: str | None = None) -> None: # Метод для редактирования значений записей в таблицах базы данных
		if where == None:
			self.sql.execute(f"UPDATE {value} FROM {table}")
		else:
			self.sql.execute(f"UPDATE {value} FROM {table} WHERE {where}")
		self.db.commit()

	@lock_and_unlock_theards
	def get_data(self, table: str, where: str = None, fetchone: bool = False, fetchall: bool = False) -> tuple | list | None: # Метод для получения данных из базы данных
		if where == None:
			self.sql.execute(f"SELECT * FROM {table}")
		else:
			self.sql.execute(f"SELECT * FROM {table} WHERE {where}")

		if fetchone:
			data: tuple = self.sql.fetchone()
		elif fetchall:
			data: list = self.sql.fetchall()
		else:
			assert Exception('Аргумент "fetchone" и "fetchall" равны False!')

		return data

if __name__ == '__main__': # Проверка, как был запущен скрипт
	raise Exception('Нельзя запускать этот скрипт как главный скрипт!')