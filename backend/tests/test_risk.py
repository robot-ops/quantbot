from app.services.risk import RiskManager

def test_calculate_position_size():
    rm = RiskManager()
    
    # Balance $10,000, 1% risk per trade ($100), 2% SL.
    # Cost = $100 / 0.02 = $5,000.
    # Price $1000 -> Size should be 5.0
    size = rm.calculate_position_size(
        current_price=1000.0,
        balance=10000.0,
        risk_per_trade_pct=1.0,
        stop_loss_pct=2.0,
        max_allocation_pct=50.0
    )
    assert size == 5.0

    # Test max allocation cap (25% of balance = $2,500).
    # If SL is tiny (0.1%), position value would be $100 / 0.001 = $100,000.
    # But it must be capped at 25% of balance ($2,500).
    # Price $10 -> Size should be 250.0
    size_capped = rm.calculate_position_size(
        current_price=10.0,
        balance=10000.0,
        risk_per_trade_pct=1.0,
        stop_loss_pct=0.1
    )
    assert size_capped == 250.0

def test_micro_balance_btc():
    rm = RiskManager()
    
    # Micro-balance test: $11 USDT balance, BTC at $65,000.
    # Should allocate ~95% of $11 ($10.45 USDT) to meet exchange $10 minimum.
    # Amount = 10.45 / 65000 = 0.000160769 -> 6 decimals = 0.000161 BTC (> 0).
    size_btc = rm.calculate_position_size(
        current_price=65000.0,
        balance=11.0,
        risk_per_trade_pct=1.0,
        stop_loss_pct=1.5,
        max_allocation_pct=25.0,
        min_order_value=10.0
    )
    assert size_btc > 0.0
    assert size_btc == 0.00016077
    assert round(size_btc * 65000.0, 2) >= 10.0

def test_check_daily_drawdown():
    rm = RiskManager()
    
    # 5% max drawdown.
    # Starting balance $10,000.
    # Equity $9,600 (4% drawdown). Should NOT trigger.
    breached, dd = rm.check_daily_drawdown(10000.0, 9600.0, 5.0)
    assert breached is False
    assert dd == 4.0

    # Equity $9,400 (6% drawdown). SHOULD trigger.
    breached_true, dd_true = rm.check_daily_drawdown(10000.0, 9400.0, 5.0)
    assert breached_true is True
    assert dd_true == 6.0

def test_evaluate_trailing_stop():
    rm = RiskManager()
    
    # Buy trade, entry $100, SL $95. Peak rises to $105.
    # Trail 2% of $105 = $2.10. New SL should be $105 - $2.10 = $102.90.
    new_sl = rm.evaluate_trailing_stop(
        entry_price=100.0,
        current_price=105.0,
        current_sl=95.0,
        side="BUY",
        trail_pct=2.0
    )
    assert new_sl == 102.90

    # Trail stop can only move up. If price drops to $103, SL should stay $102.90.
    new_sl_lower = rm.evaluate_trailing_stop(
        entry_price=100.0,
        current_price=103.0,
        current_sl=102.90,
        side="BUY",
        trail_pct=2.0
    )
    assert new_sl_lower == 102.90

def test_evaluate_break_even():
    rm = RiskManager()
    
    # Entry $100, SL $95. Break-even trigger at 1.5% profit ($101.50).
    # If price is $101.0, SL stays $95.
    new_sl_no = rm.evaluate_break_even(100.0, 101.0, 95.0, "BUY", 1.5)
    assert new_sl_no == 95.0

    # If price is $102.0, SL moves to entry ($100).
    new_sl_yes = rm.evaluate_break_even(100.0, 102.0, 95.0, "BUY", 1.5)
    assert new_sl_yes == 100.0

def test_evaluate_partial_close():
    rm = RiskManager()
    
    # Trigger target 2% profit. Price is $101. Should NOT trigger.
    should_close, ratio = rm.evaluate_partial_close(100.0, 101.0, "BUY", 2.0, False)
    assert should_close is False

    # Price is $102.5. SHOULD trigger 50% partial close.
    should_close_yes, ratio_yes = rm.evaluate_partial_close(100.0, 102.5, "BUY", 2.0, False)
    assert should_close_yes is True
    assert ratio_yes == 0.5
