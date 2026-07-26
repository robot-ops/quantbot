import os
from app.core.config import BotConfig, load_config

def test_config_initialization(test_config):
    assert test_config.symbol == "BTC/USDT"
    assert test_config.trading_mode == "demo"
    assert test_config.ema_fast == 9

def test_config_dict_export(test_config):
    d = test_config.dict()
    assert "symbol" in d
    assert d["symbol"] == "BTC/USDT"
    assert d["trading_mode"] == "demo"
