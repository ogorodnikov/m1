import os

import pytest

from core.telegram import Bot


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
    

# def test_start_handler(bot):
#     bot.start_handler(None)
    

###   Fixtures   ###

@pytest.fixture(scope="module", autouse=True)
def set_mocks(monkeypatch_module, stub):
    
    monkeypatch_module.setenv("TELEGRAM_TOKEN", "")
    
    monkeypatch_module.setattr("core.telegram.Bot.get_me", stub)
    
    monkeypatch_module.setattr("core.telegram.Bot.send_message", stub)
    monkeypatch_module.setattr("core.telegram.Bot.send_sticker", stub)
    
    
@pytest.fixture
def bot(monkeypatch, stub):

    monkeypatch.setenv("TELEGRAM_TOKEN", "")    
    monkeypatch.setattr("core.telegram.Bot.register_handlers", stub)
    
    return Bot(db=None, runner=None)
    

@pytest.fixture
def bot_with_register_handlers(monkeypatch, stub):
    
    return Bot(db=None, runner=None)