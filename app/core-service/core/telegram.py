import telebot

from threading import Thread

from core import app


telegram_token = app.config.get('TELEGRAM_TOKEN')


bot = telebot.TeleBot(telegram_token)

app.logger.info(f'BOT starting telegram bot: {bot}')


# @bot.message_handler(commands=['start', 'help'])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    
    bot_data = bot.get_me()
    bot_name = bot_data.first_name
    user_name = message.from_user.first_name
    
    app.logger.info(f'BOT /start')
    app.logger.info(f'BOT bot_data {bot_data}')
    app.logger.info(f'BOT bot_name {bot_name}')
    app.logger.info(f'BOT user_name {user_name}')

    bot.reply_to(message, f"{bot_name} welcomes you, {user_name}!")
	

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)
	
bot_polling_thread = Thread(target=bot.polling,
                            # args=(task_queue, task_results_queue, worker_active_flag),
                            daemon=True)

bot_polling_thread.start()

app.logger.info(f'BOT bot_polling_thread: {bot_polling_thread}')                                      

