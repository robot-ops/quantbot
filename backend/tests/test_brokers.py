from unittest.mock import MagicMock
from app.services.brokers import CCXTBroker, PaperBroker
from app.db.repositories import TradeRepository, OrderRepository

def test_paper_broker_balance_initialization(test_db):
    broker = PaperBroker(db=test_db, initial_balance=5000.0)
    assert broker.balance == 5000.0

def test_paper_broker_buy_execution(test_db):
    # Setup Paper Broker with underlying CCXT mock returning $10.0 per coin
    ccxt_mock = MagicMock()
    ccxt_mock.fetch_ticker.return_value = 10.0
    
    broker = PaperBroker(db=test_db, initial_balance=1000.0, fee_pct=0.1, ccxt_underlying=ccxt_mock)
    
    # Execute BUY order for 10 coins. Total cost = 10 * 10 = $100. Fee = 0.1% of 100 = $0.1. Total = $100.1
    res = broker.execute_order("BTC/USDT", "BUY", 10.0)
    
    assert res["status"] == "success"
    assert broker.balance == 899.9 # $1000 - $100.1
    
    # Check that order was saved to database
    order_repo = OrderRepository(test_db)
    orders = order_repo.get_all(mode="DEMO")
    assert len(orders) == 1
    assert orders[0].side == "BUY"
    assert orders[0].amount == 10.0
    assert orders[0].price == 10.0

def test_paper_broker_insufficient_funds(test_db):
    ccxt_mock = MagicMock()
    ccxt_mock.fetch_ticker.return_value = 1000.0
    
    broker = PaperBroker(db=test_db, initial_balance=50.0, ccxt_underlying=ccxt_mock)
    res = broker.execute_order("BTC/USDT", "BUY", 1.0)
    
    assert res["status"] == "error"
    assert "Insufficient" in res["message"]
