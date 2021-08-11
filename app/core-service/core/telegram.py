import json, jsonpickle

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from threading import Thread, enumerate as enumerate_threads

from core import app, models, runner


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
        def start_command_handler(message):
            
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
        def algorithms_command_handler(message):
            
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
                
                markup.add(InlineKeyboardButton("Open 🌻", callback_data=open_callback),
                           InlineKeyboardButton("Like 👍", callback_data=like_callback),
                           InlineKeyboardButton("Wiki 🌌", url=link))
                
                self.send_message(message.chat.id, f"{algorithm_index}) {name}", disable_notification=True)
                self.send_message(message.chat.id, f"{description}", disable_notification=True, reply_markup=markup)
                               
            app.logger.info(f'BOT /algorithms')
            
        
        @self.callback_query_handler(func=lambda call: True)
        def callback_handler(callback):

            callback_data = callback.data
            callback_query_id = callback.id                
            callback_parts = callback_data.rsplit('_', maxsplit=1)
            
            algorithm_id = callback_parts[-1]
            algorithm = models.get_algorithm(algorithm_id)
            
            algorithm_name = algorithm.get('name')
            algorithm_type = algorithm.get('type')
            algorithm_parameters = algorithm.get('parameters')
            algorithm_description = algorithm.get('description')
            
            like_callback = f"like_{algorithm_id}"
            run_classical_callback = f"run_classical_{algorithm_id}"
            run_on_simulator_callback = f"run_on_simulator_{algorithm_id}"
            run_on_quantum_device_callback = f"run_on_quantum_device_{algorithm_id}"
            
            
            if callback_data.startswith("like_"):
                
                models.like_algorithm(algorithm_id)

                flash_text = "Thank you!)"
                
            
            if callback_data.startswith("open_"):
                
                parameter_names = (parameter.get('name') for parameter in algorithm_parameters)
                parameter_names_string = ', '.join(parameter_names)
                
                text = (f"{algorithm_name}\n\n"
                        f"{algorithm_description}\n\n"
                        f"Parameters: {parameter_names_string}")
                
                markup = InlineKeyboardMarkup()
                    
                if algorithm_type == 'quantum':
                    
                    markup.row_width = 3
                    
                    markup.add(InlineKeyboardButton("Run on Simulator 🎸", callback_data=run_on_simulator_callback),
                               InlineKeyboardButton("Run on Quantum Device 🍒", callback_data=run_on_quantum_device_callback),
                               InlineKeyboardButton("Like 👍", callback_data=like_callback))

                if algorithm_type == 'classical':
                
                    markup.row_width = 2
                    
                    markup.add(InlineKeyboardButton("Run 🎺", callback_data=run_classical_callback),
                               InlineKeyboardButton("Like 👍", callback_data=like_callback))

                msg = self.send_message(callback.message.chat.id, f"{text}", reply_markup=markup)
                
                app.logger.info(f'BOT msg: {msg}')

                flash_text = "Opening..."
                
            
            if callback_data.startswith("run_classical_"):
                
                run_values = {'run_mode': 'classical'}
                
                for parameter in algorithm_parameters:
                    
                    parameter_name = parameter.get('name')
                    parameter_default_value = parameter.get('default_value')
                    
                    message_response = self.send_message(callback.message.chat.id, 
                                                         f"{parameter_name}:")
                                      
                    self.register_next_step_handler(message_response, 
                                                    self.process_parameter,
                                                    chat_identifier=callback.message.chat.id,
                                                    name=parameter_name,
                                                    default_value=parameter_default_value)
                    
                    run_values[parameter_name] = parameter_default_value
    
                task_id = runner.run_algorithm(algorithm_id, run_values)

                flash_text = "Running!"
                    
                app.logger.info(f'BOT run_values: {run_values}')    

                
            try:
                
                self.answer_callback_query(callback_query_id=callback_query_id, 
                                           text=flash_text)
                                           
            except Exception as exception:
                
                app.logger.info(f'BOT exception: {exception}')
                
                
            app.logger.info(f'BOT callback_query_id: {callback_query_id}')            
            app.logger.info(f'BOT callback_data: {callback_data}')
            
            



                
        @self.message_handler(content_types=['sticker'])
        def sticker_handler(message):
            
            file_id = message.sticker.file_id
            
            app.logger.info(f'BOT file_id: {file_id}')
            
            self.send_sticker(message.chat.id, file_id)
        	
        
        @self.message_handler(func=lambda message: True)
        def echo_all(message):
            
            app.logger.info(f'BOT message')

            self.reply_to(message, message.text)
        	
        	
    def process_parameter(self, *args, **kwargs):
        
        chat_id = kwargs.get('chat_identifier')
        name = kwargs.get('name')
        default_value = kwargs.get('default_value')
        
        self.send_message(chat_id, f"Processing {name}: {default_value}")