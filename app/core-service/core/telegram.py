import telebot

from threading import Thread, enumerate as e

from core import app, models


bot = None


def start_bot():
    
    global bot
    
    if not bot:
        
        try:
    
            telegram_token = app.config.get('TELEGRAM_TOKEN')  
                
            bot = telebot.TeleBot(telegram_token, threaded=False)
            
            register_handlers(bot)
            
            bot.infinity_polling()
            
            app.logger.info(f'BOT started telegram bot: {bot}')
            app.logger.info(f'BOT infinity_polling')

        except Exception as e:
            
            print(e)
    
    
def stop_bot():
    
    global bot
    
    if bot:

        bot.stop_bot()
        
        app.logger.info(f'BOT stop_bot: {bot}')
        
        bot.log_out()
        
        app.logger.info(f'BOT log_out: {bot}')

        bot = None
        
        app.logger.info(f'BOT None: {bot}')


def register_handlers(bot):

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
                                


