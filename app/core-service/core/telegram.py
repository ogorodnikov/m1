import telebot

from time import sleep

from threading import Thread

from core import app, models


telegram_token = app.config.get('TELEGRAM_TOKEN')  
    
bot = telebot.TeleBot(telegram_token)


def start_bot():
    
    if not bot:
    
        bot = telebot.TeleBot(telegram_token)

    bot_polling_thread = Thread(target=bot.polling,
                                # args=(polling_active_flag, ),
                                # daemon=True,
                                )

    bot_polling_thread.start()
    
    app.session['telegram_bot_state'] = 'started'
    
    app.logger.info(f'BOT started telegram bot: {bot}')
    app.logger.info(f'BOT bot_polling_thread: {bot_polling_thread}')
    
    
def stop_bot():
    
    bot.stop_bot()


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
    
    
@bot.message_handler(commands=['algorithms'])
def send_welcome(message):
    
    algorithms = models.get_all_algorithms()
    
    app.logger.info(f'BOT /algorithms')
    app.logger.info(f'BOT algorithms {algorithms}')
    
    bot.reply_to(message, f"Algorithms:")
        
    for i, algorithm in enumerate(algorithms, 1):
        
        name = algorithm['name']
        description = algorithm['description']
        link = algorithm['link']
        
        bot.send_message(message.chat.id, f"{i}) {name}", disable_notification=True)
        bot.send_message(message.chat.id, f"{description}", disable_notification=True)
        
        # bot.send_message(message.chat.id, f"{link}")
        
        # bot.reply_to(message, f"{description}")
        # bot.reply_to(message, f"{link}")
	

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)
                                

