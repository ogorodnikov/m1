import os

import pytest

from telebot import types

from core.telegram import Bot


TEST_CHAT_ID = 221192775


# def test_send_message(bot):
#     test_text = 'Test Message :)'
#     message_response = bot.send_message(TEST_CHAT_ID, test_text, 
#                                                  disable_notification=True)
#     assert message_response.message_id

def test_start(bot, monkeypatch, stub):
    

    monkeypatch.setattr("core.telegram.Bot.polling", stub)
    monkeypatch.setattr("core.telegram.Bot.stop_polling", stub)
    monkeypatch.setattr("core.telegram.Thread.start", stub)
    
    bot.start()
    
    assert os.environ['TELEGRAM_BOT_STATE'] == 'Running'
    
    
def test_stop(bot):
    
    bot.stop()
    
    assert os.environ['TELEGRAM_BOT_STATE'] == 'Stopped'
    

def test_register_handlers(bot_with_register_handlers):
    bot_with_register_handlers.register_handlers() 

# def test_start_handler(bot, message):
#     bot.start_handler(message)
    

# def test_algorithms_handler(bot, message, callback):
#     bot.algorithms_handler(message)
#     bot.algorithms_handler(callback)
    

# callback_prefixes = ['like_', 'open_', 'run_classical_', 'run_on_simulator_',
#                      'run_on_quantum_device_', 'get_algorithms']

# @pytest.mark.parametrize("prefix", callback_prefixes)
# def test_callback_handler(bot, callback, prefix):
    
#     callback.data = f"{prefix}test_algorithm"
#     bot.callback_handler(callback)

    
# @pytest.mark.parametrize("algorithm_type", ['classical', 'quantum'])
# def test_open_algorithm(bot, test_algorithm, algorithm_type):
    
#     test_algorithm['type'] = algorithm_type
    
#     bot.open_algorithm(TEST_CHAT_ID, test_algorithm)


# def test_collect_parameters(bot, message):
    
#     kwargs = {'collected_name': 'test_parameter',
#               'parameters': [{'name': 'test_parameter', 
#                               'value': 'test_parameter_value'}]}
                              
#     bot.collect_parameters(message, **kwargs)
    
    
# def test_sticker_handler(bot, sticker_message):
#     bot.sticker_handler(sticker_message)
    

# def test_echo_handler(bot, message):
#     bot.echo_handler(message)


###   Fixtures   ###

test_algorithm_data = {'id': 'test_algorithm_id',
                       'name': 'test_algorithm',
                       'link': 'https://test.com/test_algorithm',
                       'description': 'test_algorithm_description',
                       'parameters': [{'name': 'test_parameter', 
                                       'default_value': 'test_parameter_value'}]
}

class MockDB:
    
    def get_all_algorithms(self):
        return [test_algorithm_data]

    def get_algorithm(self, algorithm_id):
        return test_algorithm_data
    
    def like_algorithm(self, algorithm_id):
        pass 
    

class MockRunner:
    
    def run_algorithm(self, algorithm_id, run_values):
        task_id = 1
        return task_id
        
        
###   Fixtures   ###

@pytest.fixture(scope="module")
def set_mocks(monkeypatch_module):
    
    monkeypatch_module.setenv("TELEGRAM_TOKEN", "")
    
    
@pytest.fixture
def bot(monkeypatch, stub):
    
    monkeypatch.setattr("core.telegram.Bot.register_handlers", stub)
    
    return Bot(db=None, runner=None)
    

@pytest.fixture
def bot_with_register_handlers(monkeypatch, stub):
    
    return Bot(db=None, runner=None)
    
    
    


# @pytest.fixture(scope="module")
# def user():
#     yield types.User(id=1, is_bot=False, first_name='Test User')
    
    
# @pytest.fixture(scope="module")
# def chat():
#     yield types.Chat(id=TEST_CHAT_ID, type='private')
    
    
# @pytest.fixture(scope="module")
# def message(user, chat):
    
#     options = {'text': 'test_telegram message fixture :)'}
    
#     message = types.Message(
#         message_id=1, from_user=user, date=None, chat=chat, 
#         content_type='text', options=options, json_string=""
#     )
    
#     yield message
    

# @pytest.fixture(scope="module")
# def sticker_message(user, chat):
    
#     sticker_file_id = telegram.Bot.BUBO_CELEBRATE_STICKER_FILE_ID

#     sticker = types.Sticker(
#         file_id=sticker_file_id, file_unique_id=1, 
#         width=1, height=1, is_animated=False
#     )
    
#     options = {'sticker': sticker}
    
#     sticker_message = types.Message(
#         message_id=1, from_user=user, date=None, chat=chat, 
#         content_type='sticker', json_string="", options=options
#     )
    
#     yield sticker_message
    

# @pytest.fixture(scope="module")
# def callback(user, chat, message):

#     callback = types.CallbackQuery(
#         id=1, from_user=user, message=message, data="", chat_instance=chat
#     )

#     yield callback
    
    
# @pytest.fixture(scope="module")
# def test_algorithm():
    
#     test_algorithm_data = {'id': 'test_algorithm_id',
#                           'name': 'test_algorithm',
#                           'link': 'https://test.com/test_algorithm',
#                           'description': 'test_algorithm_description',
#                           'parameters': [{'name': 'test_parameter', 
#                                           'default_value': 'test_parameter_value'}]
#                           }
                                           
#     yield test_algorithm_data