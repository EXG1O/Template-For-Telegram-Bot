# Template For Telegram Bot
**Template For Telegram Bot** - готовый шаблон для ваших Telegram ботов.

# Содержание
- [Template For Telegram Bot](#template_for_telegram_bot)
- [Содержание](#содержание)
- [Возможности шаблона](#возможности_шаблона)
- [Установка шаблона](#установка_шаблона)
- [Список команд](#список_команд)
- [Примечание](#примечание)

# Возможности шаблона
- Добавлять неограниченное количество Telegram ботов;
- Готовый шаблон для написания своего Telegram бота, когда добавляете нового Telegram бота;
- Лёгко поддерживать ваших Telegram ботов в будущем;
- Свободно управлять вашими Telegram ботами из панели админа;
- Мониторинг пользователей, которые активировали вашего Telegram бота;
- Свободно управлять пользователями, которые активировали вашего Telegram бота.

# Установка шаблона
1. Устанавливаем **Python 3.10.7** (Установить другую версию **Python** можно спомощью программы **Python3 Installer**: https://github.com/EXG1O/Python3-Installer);
2. Устанавливаем шаблон:
```sh
git clone https://github.com/EXG1O/Template-For-Telegram-Bot.git
cd Template-For-Telegram-Bot
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
cd template_for_telegram_bot
```
3. Для запуска шаблона введите:
```sh
python3 main.py start
```
4. Если вы всё сделали правильно, то должен быть такой вывод:
```
*** Template For Telegram Bot ***
Автор: https://t.me/pycoder39

:: Введите токен Admin Telegram бота: 
```
5. Вводим токен Admin Telegram бота;
6. Создаём своих ботов, управляем ими из админ панели и радуемся 🤭.

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

# Примечание
**После того, как вы запустите шаблон в первый раз, вы не сможете использовать Admin Telegram бота, так как нужно сделать вас суперпользователем.**

Команда:
```sh
python3 main.py add_superuser
```
Вывод:
```
*** Template For Telegram Bot ***
Автор: https://t.me/pycoder39

Супер пользователь будет иметь доступ ко всем вашим Telegram ботам.
:: Введите @ пользователя: 
```