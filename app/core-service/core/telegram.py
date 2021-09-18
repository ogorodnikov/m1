from threading import Thread, enumerate as enumerate_threads

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, CallbackQuery, Message

from core import app


class Bot(TeleBot):
    
    BUBO_CELEBRATE_STICKER_FILE_ID = "CAACAgIAAxkBAAIF6GES9nEyKUKbGVt4XFzpjOeYv09dAAIUAAPp2BMo6LwZ1x6IhdYgBA"
    
    def __init__(self, *args, **kwargs):

        self.db = app.config.get('DB')
        self.runner = app.config.get('RUNNER')
        
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
        
        app.logger.info(f'BOT /algorithms')
        
        algorithms = self.db.get_all_algorithms()

        if isinstance(message_or_callback, Message):
            message = message_or_callback
        
        elif isinstance(message_or_callback, CallbackQuery):
            message = message_or_callback.message

        self.send_message(message.chat.id, f"Algorithms:", disable_notification=True)
        
            
        for algorithm_index, algorithm in enumerate(algorithms, 1):
            
            name = algorithm['name']
            link = algorithm['link']
            algorithm_id = algorithm['id']
            description = algorithm['description']
            
            open_callback = f"open_{algorithm_id}"
            like_callback = f"like_{algorithm_id}"
            
            markup = InlineKeyboardMarkup()

            markup.add(InlineKeyboardButton("Open 🌻", callback_data=open_callback),
                       InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Wiki 📖", url=link))
                       
            algorithm_text = f"<b>{algorithm_index}) {name}</b>\n\n{description}"
            
            self.send_message(message.chat.id, algorithm_text, reply_markup=markup)

    
    def callback_handler(self, callback):

        callback_data = callback.data
        callback_query_id = callback.id                
        callback_parts = callback_data.rsplit('_', maxsplit=1)
        
        app.logger.info(f'BOT callback_data: {callback_data}')
        
        algorithm_id = callback_parts[-1]
        algorithm = self.db.get_algorithm(algorithm_id)
        
        flash_text = None
        
        
        if callback_data.startswith("like_"):
            
            self.db.like_algorithm(algorithm_id)
            flash_text = "Thank you!)"
            
        
        if callback_data.startswith("open_"):
            
            chat_id = callback.message.chat.id
            self.open_algorithm(chat_id, algorithm)

        
        if callback_data.startswith("run_"):
            
            if callback_data.startswith("run_classical_"):
                run_mode = 'classical'
                
            elif callback_data.startswith("run_on_simulator_"):
                run_mode = 'simulator'

            elif callback_data.startswith("run_on_quantum_device_"):
                run_mode = 'quantum_device'
                
            algorithm_parameters = algorithm.get('parameters')

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
            

        
    def open_algorithm(self, chat_id, algorithm):
        
        app.logger.info(f'BOT open algorithm: {algorithm}')
        
        algorithm_id = algorithm.get('id')
        algorithm_name = algorithm.get('name')
        algorithm_type = algorithm.get('type')
        algorithm_link = algorithm.get('link')
        algorithm_parameters = algorithm.get('parameters')
        algorithm_description = algorithm.get('description')
        
        like_callback = f"like_{algorithm_id}"
        run_classical_callback = f"run_classical_{algorithm_id}"
        run_on_simulator_callback = f"run_on_simulator_{algorithm_id}"
        run_on_quantum_device_callback = f"run_on_quantum_device_{algorithm_id}"
        
        parameter_names = (parameter.get('name') for parameter in algorithm_parameters)
        parameter_names_string = ', '.join(parameter_names)
        
        text = (f"<b>{algorithm_name}</b>\n\n"
                f"{algorithm_description}\n\n"
                f"<b>Parameters:</b> {parameter_names_string}")
        
        markup = InlineKeyboardMarkup()
            
        if algorithm_type == 'quantum':

            markup.add(InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Wiki 📖", url=algorithm_link),
                       InlineKeyboardButton("Back 🌻", callback_data="get_algorithms"))
                       
            markup.add(InlineKeyboardButton("Run on Simulator 🎲", callback_data=run_on_simulator_callback))
            markup.add(InlineKeyboardButton("Run on Quantum Device 🌈", callback_data=run_on_quantum_device_callback))

        if algorithm_type == 'classical':
        
            markup.row_width = 3
            
            markup.add(InlineKeyboardButton("Run 🎸", callback_data=run_classical_callback),
                       InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Back 🌻", callback_data="get_algorithms"))

        self.send_message(chat_id, f"{text}", reply_markup=markup)
        

    def collect_parameters(self, message, **kwargs):

        chat_id = message.chat.id

        run_mode = kwargs.get('run_mode')        
        parameters = kwargs.get('parameters')
        algorithm_id = kwargs.get('algorithm_id')
        collected_name = kwargs.get('collected_name')

        if collected_name:
            
            collected_parameters = (parameter for parameter in parameters
                                    if parameter['name'] == collected_name)
            
            collected_parameter = next(collected_parameters)
                                       
            collected_parameter['value'] = message.text
            
        not_collected_parameters = (parameter for parameter in parameters
                                    if 'value' not in parameter)

        next_parameter = next(iter(not_collected_parameters), None)
        
        app.logger.info(f'BOT chat_id: {chat_id}')
        app.logger.info(f'BOT run_mode: {run_mode}')
        app.logger.info(f'BOT parameters: {parameters}')
        app.logger.info(f'BOT algorithm_id: {algorithm_id}')
        app.logger.info(f'BOT message.text: {message.text}')
        app.logger.info(f'BOT collected_name: {collected_name}')
        app.logger.info(f'BOT next_parameter: {next_parameter}')
        
        if next_parameter:
            self.query_next_parameter(next_parameter, chat_id, algorithm_id, run_mode, parameters)
                                            
        else:
            self.run_algorithm(chat_id, algorithm_id, run_mode, parameters)
            

    def query_next_parameter(self, next_parameter, chat_id, algorithm_id, run_mode, parameters):
    
        next_parameter_name = next_parameter.get('name')
        default_value = next_parameter.get('default_value')
        
        query_text = f"Please enter '{next_parameter_name}':"
        
        keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                              one_time_keyboard=True,
                                              input_field_placeholder=query_text)
                                           
        keyboard_markup.add(default_value)
        
        message_response = self.send_message(chat_id,
                                             query_text,
                                             reply_markup=keyboard_markup)
                          
        self.register_next_step_handler(message_response, 
                                        self.collect_parameters,
                                        run_mode=run_mode,
                                        parameters=parameters,
                                        algorithm_id=algorithm_id,
                                        collected_name=next_parameter_name)
                                        
                                        
    def run_algorithm(self, chat_id, algorithm_id, run_mode, parameters):
        
        run_values = {parameter['name']: parameter['value'] 
                      for parameter in parameters}
        
        run_values['run_mode'] = run_mode
        
        task_id = self.runner.run_algorithm(algorithm_id, run_values)
        
        app.logger.info(f'BOT algorithm_id: {algorithm_id}')
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