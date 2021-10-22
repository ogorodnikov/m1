import pytest

from telebot import types

from core import telegram


TEST_CHAT_ID = 221192775


def test_send_message(telegram_bot):
    test_text = 'Test Message :)'
    message_response = telegram_bot.send_message(TEST_CHAT_ID, test_text, 
                                                 disable_notification=True)
    assert message_response.message_id
    
    
def test_start_handler(telegram_bot, message):
    telegram_bot.start_handler(message)
    

def test_algorithms_handler(telegram_bot, message, callback):
    telegram_bot.algorithms_handler(message)
    telegram_bot.algorithms_handler(callback)
    

callback_prefixes = ['like_', 'open_', 'run_classical_', 'run_on_simulator_',
                     'run_on_quantum_device_', 'get_algorithms']

@pytest.mark.parametrize("prefix", callback_prefixes)
def test_callback_handler(telegram_bot, callback, prefix):
    
    callback.data = f"{prefix}test_algorithm"
    telegram_bot.callback_handler(callback)

    
@pytest.mark.parametrize("algorithm_type", ['classical', 'quantum'])
def test_open_algorithm(telegram_bot, test_algorithm, algorithm_type):
    
    test_algorithm['type'] = algorithm_type
    
    telegram_bot.open_algorithm(TEST_CHAT_ID, test_algorithm)


def test_collect_parameters(telegram_bot, message):
    ...
    
    
def test_sticker_handler(telegram_bot, sticker_message):
    telegram_bot.sticker_handler(sticker_message)
    

def test_echo_handler(telegram_bot, message):
    telegram_bot.echo_handler(message)
    
    
    


###   Fixtures


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

@pytest.fixture(scope="module")
def telegram_bot():
    
    mock_db = MockDB()
    runner = ...
    
    telegram_bot = telegram.Bot(mock_db, runner)
    
    telegram_bot.start()
    
    yield telegram_bot
    
    telegram_bot.stop()
    

@pytest.fixture(scope="module")
def user():
    yield types.User(id=1, is_bot=False, first_name='Test User')
    
    
@pytest.fixture(scope="module")
def chat():
    yield types.Chat(id=TEST_CHAT_ID, type='private')
    
    
@pytest.fixture(scope="module")
def message(user, chat):
    
    options = {'text': 'test_telegram message fixture :)'}
    
    message = types.Message(
        message_id=1, from_user=user, date=None, chat=chat, 
        content_type='text', options=options, json_string=""
    )
    
    yield message
    

@pytest.fixture(scope="module")
def sticker_message(user, chat):
    
    sticker_file_id = telegram.Bot.BUBO_CELEBRATE_STICKER_FILE_ID

    sticker = types.Sticker(
        file_id=sticker_file_id, file_unique_id=1, 
        width=1, height=1, is_animated=False
    )
    
    options = {'sticker': sticker}
    
    sticker_message = types.Message(
        message_id=1, from_user=user, date=None, chat=chat, 
        content_type='sticker', json_string="", options=options
    )
    
    yield sticker_message
    

@pytest.fixture(scope="module")
def callback(user, chat, message):

    callback = types.CallbackQuery(
        id=1, from_user=user, message=message, data="", chat_instance=chat
    )

    yield callback
    
    
@pytest.fixture(scope="module")
def test_algorithm():
    
    test_algorithm_data = {'id': 'test_algorithm_id',
                           'name': 'test_algorithm',
                           'link': 'https://test.com/test_algorithm',
                           'description': 'test_algorithm_description',
                           'parameters': [{'name': 'test_parameter', 
                                           'default_value': 'test_parameter_value'}]
                          }
                                           
    yield test_algorithm_data