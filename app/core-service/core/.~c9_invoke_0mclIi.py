import json, jsonpickle

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, CallbackQuery, Message

from threading import Thread, enumerate as enumerate_threads

from core import app, models, runner


BUBO_CELEBRATE_STICKER_FILE_ID = "CAACAgIAAxkBAAIF6GES9nEyKUKbGVt4XFzpjOeYv09dAAIUAAPp2BMo6LwZ1x6IhdYgBA"


class Bot(TeleBot):
    
    def __init__(self, *args, **kwargs):
        
        telegram_token = app.config.get('TELEGRAM_TOKEN')
        
        super().__init__(telegram_token, *args, 
                         parse_mode='HTML', threaded=False, **kwargs)
        
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

        self.message_handler(commands=['start'])(self.start_handler)
        self.message_handler(commands=['algorithms'])(self.algorithms_handler)
        self.message_handler(content_types=['sticker'])(self.sticker_handler)
        self.message_handler(func=lambda message: True)(self.echo_handler)

        self.callback_query_handler(func=lambda callback: callback.data.startswith("get_algorithms"))(self.algorithms_handler)
        self.callback_query_handler(func=lambda callback: True)(self.callback_handler)
        
        
    def start_handler(self, message):
        
        bot_data = self.get_me()
        bot_name = bot_data.first_name
        user_name = message.from_user.first_name
        
        app.logger.info(f'BOT /start')
        app.logger.info(f'BOT bot_data {bot_data}')
        app.logger.info(f'BOT bot_name {bot_name}')
        app.logger.info(f'BOT user_name {user_name}')
    
        self.send_message(message.chat.id, f"{bot_name} welcomes you, {user_name}!")
        
        self.send_sticker(message.chat.id, BUBO_CELEBRATE_STICKER_FILE_ID)
            

    def algorithms_handler(self, message_or_callback):
        
        algorithms = models.get_all_algorithms()
        
        if isinstance(message_or_callback, CallbackQuery):
            message = message_or_callback.message
            
        else:
            print()
            

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
            
    
    def callback_handler(self, callback):

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
            
            text = (f"<b>{algorithm_name}</b>\n\n"
                    f"{algorithm_description}\n\n"
                    f"<b>Parameters:</b> {parameter_names_string}")
            
            markup = InlineKeyboardMarkup()
                
            if algorithm_type == 'quantum':
                
                markup.row_width = 1
                
                markup.add(InlineKeyboardButton("Run on Simulator 🎲", callback_data=run_on_simulator_callback),
                           InlineKeyboardButton("Run on Quantum Device 🌈", callback_data=run_on_quantum_device_callback),
                           InlineKeyboardButton("Like 👍", callback_data=like_callback),
                           InlineKeyboardButton("Back 🌻", callback_data="get_algorithms"),
                           )

            if algorithm_type == 'classical':
            
                markup.row_width = 2
                
                markup.add(InlineKeyboardButton("Run 🎸", callback_data=run_classical_callback),
                           InlineKeyboardButton("Like 👍", callback_data=like_callback),
                           InlineKeyboardButton("Back 🌻", callback_data="get_algorithms"),
                          )

            self.send_message(callback.message.chat.id, f"{text}", reply_markup=markup)

            flash_text = "Opening..."
            
        
        if callback_data.startswith("run_"):
            
            if callback_data.startswith("run_classical_"):
                run_mode = 'classical'
                
            elif callback_data.startswith("run_on_simulator_"):
                run_mode = 'simulator'

            elif callback_data.startswith("run_on_quantum_device_"):
                run_mode = 'quantum_device'

            self.collect_parameters(parameters=algorithm_parameters,
                                    message=callback.message,
                                    algorithm_id=algorithm_id,
                                    run_mode=run_mode)
             
            flash_text = "Please enter parameters"
            
            
        if callback_data.startswith("get_algorithms"):
            
            self.algorithms_handler(callback.message)
            

        try:
            
            self.answer_callback_query(callback_query_id=callback_query_id, 
                                       text=flash_text)
                                       
        except Exception as exception:
            
            app.logger.info(f'BOT exception: {exception}')
            
            
        app.logger.info(f'BOT callback_query_id: {callback_query_id}')            
        app.logger.info(f'BOT callback_data: {callback_data}')
        
        
    
    ###   COLLECT   ###
    
        
    
    def collect_parameters(self, message, **kwargs):

        chat_id = message.chat.id

        run_mode = kwargs.get('run_mode')        
        parameters = kwargs.get('parameters')
        algorithm_id = kwargs.get('algorithm_id')
        collected_name = kwargs.get('collected_name')

        app.logger.info(f'BOT chat_id: {chat_id}')
        app.logger.info(f'BOT run_mode: {run_mode}')
        app.logger.info(f'BOT parameters: {parameters}')
        app.logger.info(f'BOT algorithm_id: {algorithm_id}')
        app.logger.info(f'BOT collected_name: {collected_name}')
        app.logger.info(f'BOT message.text: {message.text}')
        

        if collected_name:
            
            parameter = next(parameter for parameter in parameters
                             if parameter['name'] == collected_name)
                             
            parameter['value'] = message.text
            
        not_collected_parameters = (parameter for parameter in parameters
                                    if 'value' not in parameter)

        next_parameter = next(iter(not_collected_parameters), None)

        app.logger.info(f'BOT next_parameter: {next_parameter}')
        
        
        if next_parameter:
            
            self.collect_next_parameter(next_parameter, chat_id, algorithm_id, run_mode, parameters)
                                            
        else:
            
            self.run_algorithm(chat_id, algorithm_id, run_mode, parameters)
            

    def collect_next_parameter(self, next_parameter, chat_id, algorithm_id, run_mode, parameters):
    
        name = next_parameter.get('name')
        default_value = next_parameter.get('default_value')
        
        keyboard_markup = ReplyKeyboardMarkup(one_time_keyboard=True,
                                              resize_keyboard=True,
                                              row_width=3,
                                              input_field_placeholder=f"Please enter '{name}'")
                                           
        keyboard_markup.add(default_value)
        
        message_response = self.send_message(chat_id,
                                             f"Please enter '{name}':",
                                             reply_markup=keyboard_markup)
                          
        self.register_next_step_handler(message_response, 
                                        self.collect_parameters,
                                        chat_identifier=chat_id,
                                        collected_name=name,
                                        run_mode=run_mode,
                                        algorithm_id=algorithm_id,
                                        parameters=parameters)
                                        
                                        
    def run_algorithm(self, chat_id, algorithm_id, run_mode, parameters):
        
        run_values = {parameter['name']: parameter['value'] 
                      for parameter in parameters}
        
        run_values['run_mode'] = run_mode
        
        task_id = runner.run_algorithm(algorithm_id, run_values)
        
        app.logger.info(f'BOT run_values: {run_values}')
        app.logger.info(f'BOT task_id: {task_id}')
        
        domain = app.config.get('DOMAIN')
        
        task_url = f"https://{domain}/tasks?task_id={task_id}"
        
        run_message = (f"<b>Task {task_id} started:</b>\n\n"
                       f"Algorithm: {algorithm_id}\n"
                       f"Run values: {run_values}")
                       
        back_callback = f"open_{algorithm_id}"
        like_callback = f"like_{algorithm_id}"
                       
        markup = InlineKeyboardMarkup()
        
        markup.row_width = 3
        
        markup.add(InlineKeyboardButton("Open 🎸", url=task_url),
                   InlineKeyboardButton("Like 👍", callback_data=like_callback),
                   InlineKeyboardButton("Back 🌻", callback_data=back_callback))

        self.send_message(chat_id, run_message, reply_markup=markup)
    

    def sticker_handler(self, message):
        
        file_id = message.sticker.file_id
        
        app.logger.info(f'BOT file_id: {file_id}')
        
        self.send_sticker(message.chat.id, file_id)
    	

    def echo_handler(self, message):
        
        app.logger.info(f'BOT echo_handler message')

        self.reply_to(message, message.text)