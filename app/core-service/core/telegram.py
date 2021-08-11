import json, jsonpickle

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from threading import Thread, enumerate as enumerate_threads

from core import app, models


BUBO_CELEBRATE_STICKER_FILE_ID = "CAACAgIAAxkBAAIF6GES9nEyKUKbGVt4XFzpjOeYv09dAAIUAAPp2BMo6LwZ1x6IhdYgBA"


class Bot(TeleBot):
    
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
        def welcome(message):
            
            bot_data = self.get_me()
            bot_name = bot_data.first_name
            user_name = message.from_user.first_name
            
            app.logger.info(f'BOT /start')
            app.logger.info(f'BOT bot_data {bot_data}')
            app.logger.info(f'BOT bot_name {bot_name}')
            app.logger.info(f'BOT user_name {user_name}')
        
            self.send_message(message.chat.id, f"{bot_name} welcomes you, {user_name}!")
            
            self.send_sticker(message.chat.id, BUBO_CELEBRATE_STICKER_FILE_ID)
            
            
        @self.message_handler(commands=['algorithms'])
        def get_algorithms(message):
            
            algorithms = models.get_all_algorithms()

            self.send_message(message.chat.id, f"Algorithms:", disable_notification=True)
            
                
            for algorithm_index, algorithm in enumerate(algorithms, 1):
                
                algorithm_id = algorithm['id']
                name = algorithm['name']
                description = algorithm['description']
                link = algorithm['link']
                
                open_callback = f"open_{algorithm_id}"
                like_callback = f"like_{algorithm_id}"
                
                markup = InlineKeyboardMarkup()
                markup.row_width = 3
                
                markup.add(
                    InlineKeyboardButton("Open 🌻", callback_data=open_callback),
                    InlineKeyboardButton("Like 👍", callback_data=like_callback),
                    InlineKeyboardButton("Wiki 🌌", url=link)
                )
                       
                
                self.send_message(message.chat.id, f"{algorithm_index}) {name}", disable_notification=True)
                self.send_message(message.chat.id, f"{description}", disable_notification=True, reply_markup=markup)
                               
            app.logger.info(f'BOT /algorithms')

            
        
        @self.callback_query_handler(func=lambda call: True)
        def callback_handler(callback):

            callback_query_id = callback.id                
            callback_data = callback.data

            app.logger.info(f'BOT callback_query_id: {callback_query_id}')            
            app.logger.info(f'BOT callback_data: {callback_data}')

            
            if callback_data.startswith("like_"):
                
                prefix_len = len('like_')
                
                algorithm_id = callback_data[prefix_len:]
                
                models.like_algorithm(algorithm_id)

                answer = "Thank you!)"
                
            
            if callback_data.startswith("open_"):
                
                prefix_len = len('open_')
                
                algorithm_id = callback_data[prefix_len:]
                
                algorithm = models.get_algorithm(algorithm_id)
                
                algorithm_name = algorithm.get('name')
                algorithm_description = algorithm.get('description')
                algorithm_parameters = algorithm.get('parameters')
                
                self.send_message(callback.message.chat.id, f"{algorithm_name}")
                self.send_message(callback.message.chat.id, f"{algorithm_description}")
                self.send_message(callback.message.chat.id, f"Parameters:")
                
                for parameter in algorithm_parameters:
                    
                    parameter_name = parameter.get('name')
                    parameter_default_value = parameter.get('default_value')
                    
                    self.send_message(callback.message.chat.id, f"{parameter_name}: {parameter_default_value}")

                answer = "Opening..."
                
            
            self.answer_callback_query(callback_query_id=callback_query_id, 
                                       text=answer)
            
            # app.logger.info(f'BOT data {data}')

            corrected_callback = jsonpickle.encode(callback)

            callback_json = json.loads(corrected_callback)
            
            pretty_callback = json.dumps(callback_json, indent=4)
            
            # app.logger.info(f'BOT pretty_callback: {pretty_callback}')

                
        @self.message_handler(content_types=['sticker'])
        def sticker_handler(message):
            
            # corrected_message = jsonpickle.encode(message)
            # message_json = json.loads(corrected_message)
            # pretty_message = json.dumps(message_json, indent=4)
            # app.logger.info(f'BOT pretty_message: {pretty_message}')
            
            file_id = message.sticker.file_id
            
            app.logger.info(f'BOT file_id: {file_id}')
            
            self.send_sticker(message.chat.id, file_id)
        	
        
        @self.message_handler(func=lambda message: True)
        def echo_all(message):
            
            app.logger.info(f'BOT message')

            self.reply_to(message, message.text)
        	
        	
        