import json, jsonpickle

import telebot

from threading import Thread, enumerate as enumerate_threads

from core import app, models


class Bot(telebot.TeleBot):
    
    def __init__(self, *args, **kwargs):
        
        telegram_token = app.config.get('TELEGRAM_TOKEN')
        
        super().__init__(telegram_token, *args, threaded=False, **kwargs)
        
        self.register_handlers()

        app.config['TELEGRAM_BOT'] = self
        app.config['TELEGRAM_BOT_STATE'] = 'Stopped'

        app.logger.info(f'BOT initiated: {self}')
        
        
    def start(self):
        
        polling_worker_thread = Thread(target=self.polling, daemon=True)
        
        polling_worker_thread.name = "Telegram bot polling"
        polling_worker_thread.start()
        
        app.config['TELEGRAM_BOT_STATE'] = 'Started'

        app.logger.info(f'BOT polling: {self}')
        app.logger.info(f'BOT enumerate_threads: {enumerate_threads()}')


    def stop(self):
        
        self.stop_polling()
        
        app.config['TELEGRAM_BOT_STATE'] = 'Stopped'

        app.logger.info(f'BOT stop_polling: {self}')
        app.logger.info(f'BOT enumerate_threads: {enumerate_threads()}')
        

    def register_handlers(self):

        @self.message_handler(commands=['start'])
        def send_welcome(message):
            
            bot_data = self.get_me()
            bot_name = bot_data.first_name
            user_name = message.from_user.first_name
            
            app.logger.info(f'BOT /start')
            app.logger.info(f'BOT bot_data {bot_data}')
            app.logger.info(f'BOT bot_name {bot_name}')
            app.logger.info(f'BOT user_name {user_name}')
        
            self.reply_to(message, f"{bot_name} welcomes you, {user_name}!")
            
            
        @self.message_handler(commands=['algorithms'])
        def send_welcome(message):
            
            algorithms = models.get_all_algorithms()
            
            app.logger.info(f'BOT /algorithms')
            app.logger.info(f'BOT algorithms {algorithms}')

            self.send_message(message.chat.id, f"Algorithms:", disable_notification=True)
                
            for i, algorithm in enumerate(algorithms, 1):
                
                name = algorithm['name']
                description = algorithm['description']
                link = algorithm['link']
                
                self.send_message(message.chat.id, f"{i}) {name}", disable_notification=True)
                self.send_message(message.chat.id, f"{description}", disable_notification=True)
                
                # self.send_message(message.chat.id, f"{link}")
                
                # self.reply_to(message, f"{description}")
                # self.reply_to(message, f"{link}")
                
                
        @self.message_handler(content_types=['sticker'])
        def sticker_handler(message):
            
            corrected_message = jsonpickle.encode(message)

            message_json = json.loads(corrected_message)
            
            pretty_message = json.dumps(message_json, indent=4)
            
            app.logger.info(f'BOT pretty_message: {pretty_message}')
            
            file_id = message.sticker.file_id
            
            app.logger.info(f'BOT file_id: {file_id}')
            
            self.send_sticker(message.chat.id, file_id)
        	
        
        @self.message_handler(func=lambda message: True)
        def echo_all(message):
            
            app.logger.info(f'BOT message: {message}')

            # json_object = json.loads(jsonpickle.encode(message))
                        
            
            # obj = jsonpickle.encode(message)
            
            # print(type(obj))
            
            # print()
            
            # print(json.dumps(json_object, indent=2))
            
            self.reply_to(message, message.text)
        	
        	
        