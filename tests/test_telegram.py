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
    

def test_callback_handler(telegram_bot, callback):
    
    callback.data = "like_grover"

    telegram_bot.callback_handler(callback)
    
    

# @pytest.mark.skipif(should_skip, reason="No environment variables configured")


###   Fixtures


class MockDB:
    
    def get_all_algorithms(self):
        return []

    def get_algorithm(self, algorithm_id):
        return dict()
    
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
    return types.User(id=1, is_bot=False, first_name='Test User')
    
    
@pytest.fixture(scope="module")
def chat():
    return types.Chat(id=TEST_CHAT_ID, type='private')
    
    
@pytest.fixture
def message(user, chat):
    
    parameters = {'text': 'Test Text'}
    
    message = types.Message(
        message_id=1, from_user=user, date=None, chat=chat, 
        content_type='text', options=parameters, json_string="", 
    )
    
    return message
    

@pytest.fixture
def callback(user, chat, message):

    callback = types.CallbackQuery(
        id=1, from_user=user, message=message, data="", chat_instance=chat
    )

    return callback