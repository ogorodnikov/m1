import os

from telebot import TeleBot

from telebot.types import Message
from telebot.types import CallbackQuery
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

from threading import Thread

from logging import getLogger


class Bot(TeleBot):
    
    BUBO_CELEBRATE_STICKER_FILE_ID = "CAACAgIAAxkBAAIF6GES9nEyKUKbGVt4XFzpjOeYv09dAAIUAAPp2BMo6LwZ1x6IhdYgBA"
    
    def __init__(self, db, runner, *args, **kwargs):

        self.db = db
        self.runner = runner
        self.domain = os.getenv('DOMAIN')
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        
        self.logger = getLogger(__name__)

        super().__init__(self.telegram_token, *args, 
                         parse_mode='HTML', threaded=False, **kwargs)
        
        self.register_handlers()

        self.log(f'BOT initiated: {self}')
    
    
    def log(self, message):
        self.logger.info(message)
        
        
    def start(self):
        
        polling_worker_thread = Thread(target=self.polling, daemon=True)
        
        polling_worker_thread.name = "Telegram bot polling"
        polling_worker_thread.start()
        
        os.environ['TELEGRAM_BOT_STATE'] = 'Running'
        
        self.log(f'BOT polling: {self}')


    def stop(self):
        
        self.stop_polling()
        
        os.environ['TELEGRAM_BOT_STATE'] = 'Stopped'
        
        self.log(f'BOT stop_polling: {self}')


    def register_handlers(self):

        self.message_handler(commands=['start'])(self.start_handler)
        self.message_handler(commands=['algorithms'])(self.algorithms_handler)
        self.message_handler(content_types=['sticker'])(self.sticker_handler)
        self.message_handler(func=lambda message: True)(self.echo_handler)

        get_algorithms_callback_handler = self.callback_query_handler(func=(lambda callback:
                                                                            callback.data.startswith("get_algorithms")))
        get_algorithms_callback_handler(self.algorithms_handler)

        other_callback_handler = self.callback_query_handler(func=lambda callback: True)
        other_callback_handler(self.callback_handler)
        
        
    def start_handler(self, message):
        
        bot_data = self.get_me()
        bot_name = bot_data.first_name
        user_name = message.from_user.first_name
        
        self.log(f'BOT bot_data {bot_data}')
        self.log(f'BOT bot_name {bot_name}')
        self.log(f'BOT user_name {user_name}')
        self.log(f'BOT message.text {message.text}')
        self.log(f'BOT message.chat.id {message.chat.id}')
        
        github_link = f"https://github.com/ogorodnikov/m1#readme"
        
        markup = InlineKeyboardMarkup()
        
        markup.add(InlineKeyboardButton("Show algorithms 🔮", 
                                        callback_data="get_algorithms"))
        markup.add(InlineKeyboardButton("Project description 💠", url=github_link))
        
        self.send_sticker(message.chat.id, Bot.BUBO_CELEBRATE_STICKER_FILE_ID)       
        self.send_message(message.chat.id, f"{bot_name} welcomes you, {user_name}!", 
                          reply_markup=markup)
            

    def algorithms_handler(self, message_or_callback):
        
        self.log(f'BOT /algorithms')
        message = None

        if isinstance(message_or_callback, Message):
            message = message_or_callback
        
        elif isinstance(message_or_callback, CallbackQuery):
            message = message_or_callback.message

        self.send_message(message.chat.id, f"Algorithms:", disable_notification=True)

        algorithms = self.db.get_all_algorithms()        
            
        for algorithm_index, algorithm in enumerate(algorithms, 1):
            
            name = algorithm['name']
            algorithm_id = algorithm['id']
            wiki_link = algorithm['wiki_link']
            description = algorithm['description']
            
            code_link = (f"https://github.com/ogorodnikov/m1/"
                         f"tree/main/app/core-service/core/"
                         f"algorithms/{algorithm_id}.py")
            
            open_callback = f"open_{algorithm_id}"
            like_callback = f"like_{algorithm_id}"
            
            markup = InlineKeyboardMarkup(row_width=4)
            
            markup.add(InlineKeyboardButton("Open 🔮", callback_data=open_callback),
                       InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Wiki 📖", url=wiki_link),
                       InlineKeyboardButton("Code 💠", url=code_link))
                       
            algorithm_text = f"<b>{algorithm_index}) {name}</b>\n\n{description}"
            
            self.send_message(message.chat.id, algorithm_text, 
                              reply_markup=markup, disable_notification=True)

    
    def callback_handler(self, callback):

        callback_data = callback.data
        callback_query_id = callback.id                
        callback_parts = callback_data.rsplit('_', maxsplit=1)
        
        self.log(f'BOT callback_data: {callback_data}')
        
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

            run_mode = None
            
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
            self.log(f'BOT exception: {exception}')

        
    def open_algorithm(self, chat_id, algorithm):
        
        self.log(f'BOT open algorithm: {algorithm}')
        
        algorithm_id = algorithm.get('id')
        algorithm_name = algorithm.get('name')
        algorithm_type = algorithm.get('type')
        algorithm_wiki_link = algorithm.get('wiki_link')
        algorithm_parameters = algorithm.get('parameters')
        algorithm_description = algorithm.get('description')
        
        algorithm_code_link = (f"https://github.com/ogorodnikov/m1/"
                               f"tree/main/app/core-service/core/"
                               f"algorithms/{algorithm_id}.py")
        
        like_callback = f"like_{algorithm_id}"
        run_classical_callback = f"run_classical_{algorithm_id}"
        run_on_simulator_callback = f"run_on_simulator_{algorithm_id}"
        run_on_quantum_device_callback = f"run_on_quantum_device_{algorithm_id}"
        
        parameter_names = (parameter.get('name') for parameter in algorithm_parameters)
        parameter_names_string = ', '.join(parameter_names)
        
        text = (f"<b>{algorithm_name}</b>\n\n"
                f"{algorithm_description}\n\n"
                f"<b>Parameters:</b> {parameter_names_string}")
        
        markup = InlineKeyboardMarkup(row_width=4)
            
        if algorithm_type == 'quantum':

            markup.add(InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Wiki 📖", url=algorithm_wiki_link),
                       InlineKeyboardButton("Code 💠", url=algorithm_code_link))
                       
            markup.add(InlineKeyboardButton("Run on Simulator 🎲", callback_data=run_on_simulator_callback))
            markup.add(InlineKeyboardButton("Run on Quantum Device 🌈", callback_data=run_on_quantum_device_callback))
            markup.add(InlineKeyboardButton("Back to algorithms🌻", callback_data="get_algorithms"))

        if algorithm_type == 'classical':
        
            markup.row_width = 3
            
            markup.add(InlineKeyboardButton("Like 👍", callback_data=like_callback),
                       InlineKeyboardButton("Wiki 📖", url=algorithm_wiki_link),
                       InlineKeyboardButton("Code 💠", url=algorithm_code_link))

            markup.add(InlineKeyboardButton("Run 🎸", callback_data=run_classical_callback))
            markup.add(InlineKeyboardButton("Back to algorithms🌻", callback_data="get_algorithms"))

        self.send_message(chat_id, f"{text}", reply_markup=markup, 
                          disable_notification=True)
        

    def collect_parameters(self, message, **algorithm):

        chat_id = message.chat.id

        run_mode = algorithm.get('run_mode')        
        parameters = algorithm.get('parameters')
        algorithm_id = algorithm.get('algorithm_id')
        collected_name = algorithm.get('collected_name')

        if collected_name:
            
            collected_parameters = (parameter for parameter in parameters
                                    if parameter['name'] == collected_name)
            
            collected_parameter = next(collected_parameters)
                                       
            collected_parameter['value'] = message.text
            
        not_collected_parameters = (parameter for parameter in parameters
                                    if 'value' not in parameter)
                                    
        next_parameter = next(iter(not_collected_parameters), None)
        
        self.log(f'BOT chat_id: {chat_id}')
        self.log(f'BOT run_mode: {run_mode}')
        self.log(f'BOT parameters: {parameters}')
        self.log(f'BOT algorithm_id: {algorithm_id}')
        self.log(f'BOT message.text: {message.text}')
        self.log(f'BOT collected_name: {collected_name}')
        self.log(f'BOT next_parameter: {next_parameter}')
        
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
        
        self.log(f'BOT algorithm_id: {algorithm_id}')
        self.log(f'BOT run_values: {run_values}')
        self.log(f'BOT task_id: {task_id}')
        
        task_url = f"https://{self.domain}/tasks?task_id={task_id}"
        
        run_message = (f"<b>Task {task_id} started:</b>\n\n"
                       f"Algorithm: {algorithm_id}\n"
                       f"Run values: {run_values}")
                       
        back_callback = f"open_{algorithm_id}"
        like_callback = f"like_{algorithm_id}"
                       
        markup = InlineKeyboardMarkup()
        
        markup.row_width = 3
        
        markup.add(InlineKeyboardButton("Show task execution 🔮", url=task_url))
        markup.add(InlineKeyboardButton("Like 👍", callback_data=like_callback))
        markup.add(InlineKeyboardButton("Back to algorithm 🌻", callback_data=back_callback))

        self.send_message(chat_id, run_message, reply_markup=markup)
    

    def sticker_handler(self, message):
        
        file_id = message.sticker.file_id
        
        self.log(f'BOT sticker_handler file_id: {file_id}')
        self.send_sticker(message.chat.id, file_id, disable_notification=True)


    def echo_handler(self, message):
        
        self.log(f'BOT echo_handler message.json: {message.json}')

        print("message:", message)
        print("message.json:", message.json)
        print("message.text:", message.text)
        print("self.reply_to:", self.reply_to)

        # self.reply_to(message, message.text, disable_notification=True)

        self.send_message(message.chat.id, message, disable_notification=True)
