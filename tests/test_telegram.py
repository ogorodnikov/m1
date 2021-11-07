import os

import pytest

from telebot import types

from core.telegram import Bot
from core.dynamo import Dynamo
from core.runner import Runner


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
    

def test_start_handler(bot, message):
    bot.start_handler(message=message)
    

def test_algorithms_handler(bot, message, callback):
    bot.algorithms_handler(message)
    bot.algorithms_handler(callback)


callback_prefixes = ['like_', 'open_', 'run_classical_', 'run_on_simulator_',
                     'run_on_quantum_device_', 'get_algorithms']

@pytest.mark.parametrize("prefix", callback_prefixes)
def test_callback_handler(bot, prefix, callback, monkeypatch, stub):
    
    monkeypatch.setattr("core.telegram.Bot.open_algorithm", stub)
    monkeypatch.setattr("core.telegram.Bot.collect_parameters", stub)
    monkeypatch.setattr("core.telegram.Bot.algorithms_handler", stub)
    monkeypatch.setattr("core.telegram.Bot.answer_callback_query", stub)
    
    callback.data = f"{prefix}test_algorithm"
    
    bot.callback_handler(callback)


def test_callback_handler_exception(bot, callback, monkeypatch, warn):
    
    monkeypatch.setattr("core.telegram.Bot.answer_callback_query", warn)
    
    bot.callback_handler(callback)
    

@pytest.mark.parametrize("algorithm_type", ['classical', 'quantum'])
def test_open_algorithm(bot, test_algorithm, algorithm_type):
    
    test_algorithm['type'] = algorithm_type
    
    bot.open_algorithm(chat_id=None, algorithm=test_algorithm)


@pytest.mark.parametrize("algorithm_type", ['classical', 'quantum'])
def test_open_algorithm(bot, test_algorithm, algorithm_type):
    
    test_algorithm['type'] = algorithm_type
    
    bot.open_algorithm(chat_id=None, algorithm=test_algorithm)
    

def test_collect_parameters_run(bot, monkeypatch, stub, message):
    
    test_algorithm = {'collected_name': 'collected_parameter',
                      'parameters': [{'name': 'collected_parameter', 
                                      'value': 'collected_value'}]}
                              
    monkeypatch.setattr("core.telegram.Bot.run_algorithm", stub)
                              
    bot.collect_parameters(message, **test_algorithm)


def test_collect_parameters_next(bot, monkeypatch, stub, message):
    
    test_algorithm = {'collected_name': 'collected_parameter',
                      'parameters': [{'name': 'collected_parameter', 
                                      'value': 'collected_value'},
                                     {'name': 'not_collected_parameter'}]}
                              
    monkeypatch.setattr("core.telegram.Bot.query_next_parameter", stub)
                              
    bot.collect_parameters(message, **test_algorithm)
    
    
def test_query_next_parameter(bot, monkeypatch, stub):
    
    monkeypatch.setattr("core.telegram.Bot.register_next_step_handler", stub)
    
    bot.query_next_parameter(next_parameter={'default_value': ''}, 
                             chat_id=None, 
                             algorithm_id=None, 
                             run_mode=None, 
                             parameters=None)
    

def test_run_algorithm(bot):
    
    bot.run_algorithm(chat_id=None, 
                      algorithm_id=None, 
                      run_mode=None, 
                      parameters=[])
       
    
###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(monkeypatch_module, user, stub, test_algorithm):
    
    monkeypatch_module.setenv("TELEGRAM_TOKEN", "")
    
    monkeypatch_module.setattr("core.telegram.Bot.get_me", lambda self: user)
    
    monkeypatch_module.setattr("core.telegram.Bot.send_message", stub)
    monkeypatch_module.setattr("core.telegram.Bot.send_sticker", stub)
    
    monkeypatch_module.setattr(Runner, "__init__", stub)
    monkeypatch_module.setattr(Runner, "run_algorithm", stub)
    
    monkeypatch_module.setattr(Dynamo, "__init__", stub) 
    monkeypatch_module.setattr(Dynamo, "like_algorithm", stub) 
    
    monkeypatch_module.setattr(Dynamo, "get_algorithm",
                               lambda self, algorithm_id: test_algorithm) 
    monkeypatch_module.setattr(Dynamo, "get_all_algorithms", 
                               lambda self: [test_algorithm])
    
    
@pytest.fixture
def bot(monkeypatch, stub):

    monkeypatch.setenv("TELEGRAM_TOKEN", "")    
    monkeypatch.setattr("core.telegram.Bot.register_handlers", stub)
    
    return Bot(db=Dynamo(), runner=Runner())
    

@pytest.fixture
def bot_with_register_handlers(monkeypatch, stub):
    
    return Bot(db=None, runner=None)
    

###   Type fixtures   ###

@pytest.fixture(scope="module")
def user():
    yield types.User(id=1, is_bot=False, first_name='Test User')


@pytest.fixture(scope="module")
def chat():
    yield types.Chat(id=None, type='private')
    
    
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
    
    sticker_file_id = Bot.BUBO_CELEBRATE_STICKER_FILE_ID

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


test_algorithm_data = {'id': 'test_algorithm_id',
                   'name': 'test_algorithm',
                   'link': 'https://test.com/test_algorithm',
                   'description': 'test_algorithm_description',
                   'parameters': [{'name': 'test_parameter', 
                                   'default_value': 'test_parameter_value'}]
}

@pytest.fixture(scope="module")
def test_algorithm():
    return test_algorithm_data
    