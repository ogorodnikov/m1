import pytest

from telebot import types

from core.telegram import Bot

from test_telegram import user
from test_telegram import test_algorithm

from test_telegram import test_algorithm_data


TEST_CHAT_ID = 221192775


###   Telegram   ###

def test_send_message(telegram_bot):
    test_text = 'Test Message :)'
    message_response = telegram_bot.send_message(TEST_CHAT_ID, test_text, 
                                                 disable_notification=True)
    assert message_response.message_id
    
    
def test_start_handler(telegram_bot, test_message):
    telegram_bot.start_handler(test_message)
    

def test_algorithms_handler(telegram_bot, test_message, test_callback):
    telegram_bot.algorithms_handler(test_message)
    telegram_bot.algorithms_handler(test_callback)
    

callback_prefixes = ['like_', 'open_', 'run_classical_', 'run_on_simulator_',
                     'run_on_quantum_device_', 'get_algorithms']

@pytest.mark.parametrize("prefix", callback_prefixes)
def test_callback_handler(telegram_bot, test_callback, prefix):
    
    test_callback.data = f"{prefix}test_algorithm"
    telegram_bot.callback_handler(test_callback)

    
@pytest.mark.parametrize("algorithm_type", ['classical', 'quantum'])
def test_open_algorithm(telegram_bot, test_algorithm, algorithm_type):
    
    test_algorithm['type'] = algorithm_type
    
    telegram_bot.open_algorithm(TEST_CHAT_ID, test_algorithm)


def test_collect_parameters(telegram_bot, test_message):
    
    kwargs = {'collected_name': 'test_parameter',
              'parameters': [{'name': 'test_parameter', 
                              'value': 'test_parameter_value'}]}
                              
    telegram_bot.collect_parameters(test_message, **kwargs)
    
    
def test_sticker_handler(telegram_bot, test_sticker_message):
    telegram_bot.sticker_handler(test_sticker_message)
    

def test_echo_handler(telegram_bot, test_message):
    telegram_bot.echo_handler(test_message)


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
def test_chat():
    yield types.Chat(id=TEST_CHAT_ID, type='private')


@pytest.fixture(scope="module")
def test_message(user, test_chat):
    
    options = {'text': 'Test Chat Message fixture :)'}
    
    test_message = types.Message(
        message_id=1, from_user=user, date=None, chat=test_chat, 
        content_type='text', options=options, json_string=""
    )
    
    yield test_message
    

@pytest.fixture(scope="module")
def test_callback(user, test_chat, test_message):

    test_callback = types.CallbackQuery(
        id=1, from_user=user, message=test_message, 
        data="", chat_instance=test_chat,
        json_string="")

    yield test_callback
    

@pytest.fixture(scope="module")
def test_sticker_message(user, test_chat):
    
    sticker_file_id = Bot.BUBO_CELEBRATE_STICKER_FILE_ID

    sticker = types.Sticker(
        file_id=sticker_file_id, file_unique_id=1,
        type="regular", width=1, height=1,
        is_animated=False, is_video=False,
    )
    
    options = {'sticker': sticker}
    
    test_sticker_message = types.Message(
        message_id=1, from_user=user, date=None, chat=test_chat, 
        content_type='sticker', json_string="", options=options
    )
    
    yield test_sticker_message