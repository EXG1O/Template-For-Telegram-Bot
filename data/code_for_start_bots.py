from telegram_bots.template.bot import TemplateTelegramBot

template_telegram_bot = TemplateTelegramBot(telegram_bot[1].capitalize())
th = Thread(target=template_telegram_bot.start)
th.start()