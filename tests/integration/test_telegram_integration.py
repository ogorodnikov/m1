import pytest

from telebot import types

from core.telegram import Bot

from test_telegram import user
from test_telegram import message
from test_telegram import sticker_message
from test_telegram import callback
from test_telegram import test_algorithm
from test_telegram import set_mocks

from test_telegram import test_algorithm_data


TEST_CHAT_ID = 221192775


###   Telegram   ###

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
    
    kwargs = {'collected_name': 'test_parameter',
              'parameters': [{'name': 'test_parameter', 
                              'value': 'test_parameter_value'}]}
                              
    telegram_bot.collect_parameters(message, **kwargs)
    
    
def test_sticker_handler(telegram_bot, sticker_message):
    telegram_bot.sticker_handler(sticker_message)
    

def test_echo_handler(telegram_bot, message):
    telegram_bot.echo_handler(message)


###   Fixtures   ###

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

        

@pytest.fixture(scope="module")
def telegram_bot(run_config):
    
    mock_db = MockDB()
    runner = MockRunner()
    
    telegram_bot = Bot(mock_db, runner)
    
    telegram_bot.start()
    
    yield telegram_bot
    
    telegram_bot.stop()
    

###   Type fixtures override   ###

@pytest.fixture(scope="module")
def chat():
    yield types.Chat(id=TEST_CHAT_ID, type='private')