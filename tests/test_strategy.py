from src.services.strategy import Strategy


def test_bullish_not_owned_score_ge_70_returns_buy():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bullish",
            "price": 155.0,
            "sma_20": 150.0,
            "sma_50": 145.0,
            "avg_volume": 1000000,
            "score": 80,
        }
    ]

    decisions = strategy.evaluate_scan_results(scan_results)

    assert decisions == [
        {"symbol": "AAPL", "action": "buy", "reason": "bullish and above score threshold", "score": 80}
    ]


def test_bullish_owned_returns_hold():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bullish",
            "price": 155.0,
            "sma_20": 150.0,
            "sma_50": 145.0,
            "avg_volume": 1000000,
            "score": 90,
        }
    ]
    broker_positions = [{"symbol": "AAPL", "quantity": 10, "average_entry_price": 148.0}]

    decisions = strategy.evaluate_scan_results(scan_results, broker_positions=broker_positions)

    assert decisions == [
        {"symbol": "AAPL", "action": "hold", "reason": "owned and bullish", "score": 90}
    ]


def test_bearish_owned_returns_sell():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bearish",
            "price": 155.0,
            "sma_20": 150.0,
            "sma_50": 160.0,
            "avg_volume": 1000000,
            "score": 20,
        }
    ]
    broker_positions = [{"symbol": "AAPL", "quantity": 10, "average_entry_price": 148.0, "stop_loss": 145.0}]

    decisions = strategy.evaluate_scan_results(scan_results, broker_positions=broker_positions)

    assert decisions == [
        {"symbol": "AAPL", "action": "sell", "reason": "owned and bearish", "score": 20}
    ]


def test_owned_symbol_below_stop_loss_returns_sell():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bullish",
            "price": 93.0,
            "sma_20": 90.0,
            "sma_50": 85.0,
            "avg_volume": 1000000,
            "score": 90,
        }
    ]
    broker_positions = [{"symbol": "AAPL", "quantity": 10, "average_entry_price": 100.0, "stop_loss": 95.0}]

    decisions = strategy.evaluate_scan_results(scan_results, broker_positions=broker_positions)

    assert decisions == [
        {"symbol": "AAPL", "action": "sell", "reason": "stop loss hit", "score": 90}
    ]


def test_owned_symbol_below_trailing_stop_returns_sell():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bullish",
            "price": 92.0,
            "sma_20": 90.0,
            "sma_50": 85.0,
            "avg_volume": 1000000,
            "score": 90,
        }
    ]
    broker_positions = [{"symbol": "AAPL", "quantity": 10, "average_entry_price": 100.0, "stop_loss": 80.0, "trailing_stop": 95.0}]

    decisions = strategy.evaluate_scan_results(scan_results, broker_positions=broker_positions)

    assert decisions == [
        {"symbol": "AAPL", "action": "sell", "reason": "trailing stop hit", "score": 90}
    ]


def test_bullish_not_owned_score_lt_70_returns_ignore():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "AAPL",
            "trend_state": "bullish",
            "price": 155.0,
            "sma_20": 150.0,
            "sma_50": 145.0,
            "avg_volume": 1000000,
            "score": 65,
        }
    ]

    decisions = strategy.evaluate_scan_results(scan_results)

    assert decisions == [
        {"symbol": "AAPL", "action": "ignore", "reason": "does not meet buy conditions", "score": 65}
    ]


def test_bearish_or_invalid_stock_returns_ignore():
    strategy = Strategy(settings={})
    scan_results = [
        {
            "symbol": "TSLA",
            "trend_state": "bearish",
            "price": 650.0,
            "sma_20": 700.0,
            "sma_50": 710.0,
            "avg_volume": 500000,
            "score": 30,
        },
        {
            "symbol": "MSFT",
            "trend_state": "bullish",
            "price": 300.0,
            "sma_20": 310.0,
            "sma_50": 315.0,
            "avg_volume": 400000,
            "score": 40,
        },
        {
            "symbol": None,
            "trend_state": "bullish",
            "price": 100.0,
            "sma_20": 90.0,
            "sma_50": 95.0,
            "avg_volume": 100000,
            "score": 100,
        },
    ]

    decisions = strategy.evaluate_scan_results(scan_results)

    assert decisions == [
        {"symbol": "TSLA", "action": "ignore", "reason": "does not meet buy conditions", "score": 30},
        {"symbol": "MSFT", "action": "ignore", "reason": "does not meet buy conditions", "score": 40},
        {"symbol": None, "action": "ignore", "reason": "invalid symbol", "score": 100},
    ]
