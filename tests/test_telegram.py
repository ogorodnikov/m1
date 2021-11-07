import os

import pytest

from core.telegram import Bot
from core.dynamo import Dynamo
from core.runner import Runner

from integration.test_telegram_integration import user
from integration.test_telegram_integration import chat
from integration.test_telegram_integration import message
from integration.test_telegram_integration import sticker_message
from integration.test_telegram_integration import callback
from integration.test_telegram_integration import test_algorithm


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
    

###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(monkeypatch_module, user, stub, test_algorithm):
    
    monkeypatch_module.setenv("TELEGRAM_TOKEN", "")
    
    monkeypatch_module.setattr("core.telegram.Bot.get_me", lambda self: user)
    
    monkeypatch_module.setattr("core.telegram.Bot.send_message", stub)
    monkeypatch_module.setattr("core.telegram.Bot.send_sticker", stub)
    
    monkeypatch_module.setattr(Runner, "__init__", stub)
    
    monkeypatch_module.setattr(Dynamo, "__init__", stub) 
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
    

