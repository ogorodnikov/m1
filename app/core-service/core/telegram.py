import telebot, json, jsonpickle, time

from threading import Thread, Event, enumerate as e

from core import app, models


class Bot(telebot.TeleBot):
    
    def __init__(self, *args, **kwargs):
        
        telegram_token = app.config.get('TELEGRAM_TOKEN')
        
        super().__init__(telegram_token, *args, threaded=False, **kwargs)
        
        self.register_handlers()
        
        self.is_polling = Event()
        
        app.config['TELEGRAM_BOT'] = self
        app.config['TELEGRAM_BOT_STATE'] = 'Stopped'

        app.logger.info(f'BOT initiated: {self}')
        
        
    def polling_worker(self):
        
        while self.is_polling.is_set():
            
            self.polling()
            
            
            # time.sleep(1)
            
            # app.logger.info(f'BOT polling')
        
            # updates = self.get_updates()
            
            # app.logger.info(f'BOT updates: {updates}')
            
            # self.process_new_updates(updates)
            
            
        app.logger.info(f'BOT exit thread')
        
        
    def start(self):
        
        self.is_polling.set()
        
        polling_worker_thread = Thread(target=self.polling, daemon=True)
        
        polling_worker_thread.name = "Telegram bot polling"
                                              
        polling_worker_thread.start()
        
        app.config['TELEGRAM_BOT_STATE'] = 'Started'

        app.logger.info(f'BOT polling: {self}')
        app.logger.info(f'BOT e: {e()}')
        
        
        # self.polling()
        

    def stop(self):
        
        self.is_polling.clear()
        
        self.stop_polling()
        
        app.config['TELEGRAM_BOT_STATE'] = 'Stopped'

        app.logger.info(f'BOT stop_polling: {self}')
        app.logger.info(f'BOT e: {e()}')
        
        
        # self.stop_polling()        


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
            
            # jsonpickle_encode = jsonpickle.encode(message)
            
            # jsonpickle_encode = str(message).replace('\'', "\"")
            
            # json_loads = json.loads(jsonpickle_encode)
            
            # json_dumps = json.dumps(json_loads)
            
            
            # app.logger.info(f'BOT sticker: {message}')
            
            # print()
            # print()
            # print()
            
            # app.logger.info(f'BOT jsonpickle_encode: {jsonpickle_encode}')
            # app.logger.info(f'BOT type(jsonpickle_encode): {type(jsonpickle_encode)}')
            
            # print()
            # print()
            # print()
            
            # app.logger.info(f'BOT json_loads: {json_loads}')
            # app.logger.info(f'BOT type(json_loads): {type(json_loads)}')
            
            # print()
            # print()
            # print()
            
            # app.logger.info(f'BOT json_dumps: {json_dumps}')
            # app.logger.info(f'BOT type(json_dumps): {type(json_dumps)}')
            
            # print()
            # print()
            # print()
            
            self.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIELWESyucWhUpjyAk_M0IPJtJ66j3mAAIEAAPp2BMoj43WIG9piJkgBA')
        	
        
        @self.message_handler(func=lambda message: True)
        def echo_all(message):
            
            app.logger.info(f'BOT message: {message}')
            
            print(message.json)
            
            json_object = json.loads(jsonpickle.encode(message))
                        
            
            # obj = jsonpickle.encode(message)
            
            # print(type(obj))
            
            print()
            
            print(json.dumps(json_object, indent=2))
            
            self.reply_to(message, message.text)
        	
        	
        