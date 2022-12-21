# Template For Telegram Bot
**Template For Telegram Bot** - готовый шаблон для ваших Telegram ботов.

# Содержание
- [Template For Telegram Bot](#template-for-telegram-bot)
- [Содержание](#содержание)
- [Возможности шаблона](#возможности-шаблона)
- [Установка шаблона](#установка-шаблона)
- [Список команд](#список-команд)

# Возможности шаблона
- Добавлять неограниченное количество Telegram ботов;
- Готовый шаблон для написания своего Telegram бота, когда добавляете нового Telegram бота;
- Лёгко поддерживать ваших Telegram ботов в будущем;
- Свободно управлять вашими Telegram ботами из панели админа;
- Мониторинг пользователей, которые активировали вашего Telegram бота;
- Свободно управлять пользователями, которые активировали вашего Telegram бота.

# Установка и запуск шаблона
1. Устанавливаем **Python 3.10.7** (Установить другую версию **Python** можно спомощью программы **Python3 Installer**: https://github.com/EXG1O/Python3-Installer);
2. Устанавливаем шаблон:
```sh
git clone https://github.com/EXG1O/Template-For-Telegram-Bot.git
cd Template-For-Telegram-Bot
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
3. Для запуска шаблона введите:
```sh
python3 main.py start
```
4. Вводим токен Admin Telegram бота:
```
*** Template For Telegram Bot ***
Автор: https://t.me/pycoder39

:: Введите токен Admin Telegram бота: 
```
5. Вводим @ пользователя:
```
*** Template For Telegram Bot ***
Автор: https://t.me/pycoder39

:: Введите токен Admin Telegram бота: test1234512345

Для того, чтобы вы могли пользоваться Admin Telegram ботом, добавьте себя в список суперпользователей!
Супер пользователь будет иметь доступ ко всем вашим Telegram ботам!
:: Введите @ пользователя:
```
6. Если вы всё ввели правильно, то вывод будет такой:
```
*** Template For Telegram Bot ***
Автор: https://t.me/pycoder39

:: Введите токен Admin Telegram бота: test1234512345

Для того, чтобы вы могли пользоваться Admin Telegram ботом, добавьте себя в список суперпользователей!
Супер пользователь будет иметь доступ ко всем вашим Telegram ботам!
:: Введите @ пользователя: @pycoder39

Добавления суперпользователя...
Вы успешно добавили суперпользователья @pycoder39.

Запуск Telegram ботов...
Admin Telegram бот успешно запущен.
```
7. Создаём своих ботов, управляем ими из админ панели и радуемся 🤭.

# Список команд
1. **help** - Вывод всех команд;
2. **start** - Запуск всех ваших Telegram ботов;
3. **add_telegram_bot** - Добавления Telegram бота;
4. **delete_telegram_bot** - Удаления Telegram бота;
5. **add_superuser** - Добавления суперпользователя;
6. **delete_superuser** - Удаления суперпользователя;
7. **clear** - Удаление всех ваших Telegram ботов.
```
python3 main.py command👆️
```