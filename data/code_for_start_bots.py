from telegram_bots.template.bot import TemplateTelegramBot

template_telegram_bot = TemplateTelegramBot(telegram_bot_name.capitalize())
th = Thread(target=template_telegram_bot.start)
th.start()

telegram_bots = TelegramBots().telegram_bots
telegram_bots.update({'template': template_telegram_bot})