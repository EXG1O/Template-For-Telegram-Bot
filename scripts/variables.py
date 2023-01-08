from threading import Lock

# Многопоточный Singleton
class SingletonMeta(type):
	_instances = {}
	_lock = Lock()

	def __call__(cls, *args, **kwargs):
		with cls._lock:
			if cls not in cls._instances:
				instance = super().__call__(*args, **kwargs)
				cls._instances[cls] = instance
		return cls._instances[cls]

# Класс Variables
class Variables(metaclass=SingletonMeta):
	telegram_bots = {}
	unique_key = ''