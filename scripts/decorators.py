import telegram

from datetime import datetime

def check_user(func) -> None: # Декоратор для проверки доступа пользователя к данному боту
    def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
        chat_id, user_id, username = update.effective_chat.id, update.effective_user.id, update.effective_user.name

        user: tuple | None = self.db.get_data(table=f'{self.telegram_bot_name}TelegramBotUsers', where=f"user_id='{user_id}'", fetchone=True)
        superuser: tuple | None = self.db.get_data(table='Superusers', where=f"username='{username}'", fetchone=True)
        if user == None:
            values = (
                user_id,
                chat_id,
                username,
                str(datetime.now()).split('.')[0],
                0 if self.config[f'{self.telegram_bot_name}TelegramBot']['Private'] == '1' else 1
            )
            self.db.insert_into(table=f'{self.telegram_bot_name}TelegramBotUsers', values=values)

            if superuser == None:
                self.config.read('./data/config.ini')
                if self.config[f'{self.telegram_bot_name}TelegramBot']['Private'] == '1':
                    context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, ожидайте пока вам разрешат им пользоваться.')
                else:
                    context.bot.send_message(chat_id=chat_id, text='Вы успешно добавленны в базу данных пользователей данного бота, и можете пользоваться ботом.')

        if superuser == None:
            if user != None:
                self.config.read('./data/config.ini')
                if user[4] == 1 or self.config[f'{self.telegram_bot_name}TelegramBot']['Private'] == '0':
                    func(self, update, context)
                else:
                    context.bot.send_message(chat_id=chat_id, text='Вы не имеете доступ к данному боту!')
        else:
            func(self, update, context)
    wrapper.__name__ = func.__name__
    return wrapper

def get_user_data(arugments_list: list) -> None: # Декоратор для получения необходимой информации
    def decorator(func):
        def wrapper(self, update: telegram.update.Update, context: telegram.ext.callbackcontext.CallbackContext):
            arugments = {
                'update': update,
                'context': context,
                'user_id': update.effective_user.id,
                'chat_id': update.effective_chat.id,
                'username': update.effective_user.username,
                'message_id': update.effective_message.message_id
            }
            if update.callback_query != None:
                arugments.update({'callback_data': update.callback_query.data})

            arugments_dict = {'self': self}
            for arugment in arugments_list:
                if arugment in arugments:
                    arugments_dict.update({arugment: arugments[arugment]})
            func(**arugments_dict)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator