import telebot

from time import sleep

from threading import Thread, Event, enumerate as e

from core import app, models


telegram_token = app.config.get('TELEGRAM_TOKEN')


bot = telebot.TeleBot(telegram_token, threaded=False)

app.logger.info(f'BOT starting telegram bot: {bot}')

polling_active_flag = Event()
polling_active_flag.set()


def bot_polling_worker(polling_active_flag):
    
    while True:
        
        sleep(1)
        
        polling_active_flag.wait()
        
        bot.get_updates()
        
        app.logger.info(f'BOT get_updates()')
        


def start_bot_polling():
    
    # bot_polling_thread = Thread(target=bot_polling_worker,
    #                             args=(polling_active_flag, ),
    #                             # daemon=True,
    #                             )
    
    bot_polling_thread = Thread(
                            target=bot.polling,
                            # args=(polling_active_flag, ),
                            # daemon=True,
                            )

    bot_polling_thread.start()
    
    # bot.polling()
    
    app.logger.info(f'BOT bot_polling_thread: {bot_polling_thread}')

    

def pause_bot_polling():
    
    bot.__stop_polling.set()
    
    app.logger.info(f'BOT pause_bot_polling')
    
    
def resume_bot_polling():
    
    bot.__stop_polling.clear()
    
    app.logger.info(f'BOT resume_bot_polling')    
    
    
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
                                

