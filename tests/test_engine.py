from src.engine import TradingEngine


class FakeMarketDataProvider:
    def __init__(self, scan_results):
        self.scan_results = scan_results

    def get_watchlist(self, settings):
        return [entry["symbol"] for entry in self.scan_results]

    def get_current_price(self, symbol):
        for entry in self.scan_results:
            if entry["symbol"] == symbol:
                return entry["price"]
        return 0.0

    def get_historical(self, symbol, days):
        for entry in self.scan_results:
            if entry["symbol"] == symbol:
                if entry.get("trend_state") == "bearish":
                    # decreasing trend results in sma_20 < sma_50
                    start = 200
                    return [
                        {"close": float(start - i), "volume": float(entry.get("avg_volume", 1) + i)}
                        for i in range(days)
                    ]

                # ascending trend to make sma_20 > sma_50 and trend bullish.
                start = 100
                return [
                    {"close": float(start + i), "volume": float(entry.get("avg_volume", 1) + i)}
                    for i in range(days)
                ]
        return []


def test_bullish_scan_triggers_buy():
    scan_results = [
        {"symbol": "AAPL", "trend_state": "bullish", "price": 200.0, "sma_20": 190.0, "avg_volume": 1000},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    report = engine.run_cycle()

    assert report["balance"] == 1000 - 200.0
    assert report["positions"][0]["symbol"] == "AAPL"
    assert report["positions"][0]["quantity"] == 1
    assert len(report["trade_history"]) == 1
    assert report["decisions"][0]["action"] == "buy"
    assert report["notifications"][0] == "BUY AAPL at 200.0"
    assert report["notifications"][-1] == report["summary"]


def test_owned_bullish_returns_hold_no_duplicate_buy():
    scan_results = [
        {"symbol": "AAPL", "trend_state": "bullish", "price": 200.0, "sma_20": 190.0, "avg_volume": 1000},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    # seed position manually
    engine.broker.buy(symbol="AAPL", price=200.0, quantity=1)

    report = engine.run_cycle()

    assert report["balance"] == 1000 - 200.0
    assert len(report["trade_history"]) == 1  # no new buy
    assert report["decisions"][0]["action"] == "hold"


def test_ignored_symbol_does_not_trade():
    scan_results = [
        {"symbol": "TSLA", "trend_state": "bearish", "price": 600.0, "sma_20": 650.0, "avg_volume": 1000},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    report = engine.run_cycle()

    assert report["balance"] == 1000
    assert report["positions"] == []
    assert report["trade_history"] == []
    assert report["decisions"][0]["action"] == "ignore"
    assert report["notifications"][-1] == report["summary"]


def test_owned_bearish_symbol_triggers_full_sell():
    scan_results = [
        {"symbol": "AAPL", "trend_state": "bearish", "price": 190.0, "sma_20": 195.0, "avg_volume": 1000},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    engine.broker.buy(symbol="AAPL", price=200.0, quantity=2)

    report = engine.run_cycle()

    assert report["decisions"][0]["action"] == "sell"
    assert report["trade_history"][-1]["side"] == "sell"
    assert report["positions"] == []
    assert report["notifications"][-2] == "SELL AAPL at 190.0"
    assert "summary" in report
    assert report["notifications"][-1] == report["summary"]


def test_engine_stop_loss_sell_sends_stop_loss_notification():
    scan_results = [
        {"symbol": "AAPL", "trend_state": "bullish", "price": 188.0, "sma_20": 190.0, "avg_volume": 1000, "score": 90},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    engine.broker.buy(symbol="AAPL", price=200.0, quantity=2, stop_loss=190.0)

    report = engine.run_cycle()

    assert report["decisions"][0]["action"] == "sell"
    assert report["trade_history"][-1]["side"] == "sell"
    assert report["positions"] == []
    assert report["notifications"][-2] == "SELL AAPL at 188.0 (STOP LOSS)"
    assert report["notifications"][-1] == report["summary"]


def test_engine_trailing_stop_sell_sends_trailing_notification():
    scan_results = [
        {"symbol": "AAPL", "trend_state": "bullish", "price": 108.0, "sma_20": 105.0, "avg_volume": 1000, "score": 90},
    ]
    provider = FakeMarketDataProvider(scan_results)
    engine = TradingEngine(settings={"starting_cash": 1000}, market_data_provider=provider)

    engine.broker.buy(symbol="AAPL", price=100.0, quantity=2, stop_loss=80.0)
    engine.broker.update_position_price(symbol="AAPL", current_price=120.0)

    report = engine.run_cycle()

    assert report["decisions"][0]["action"] == "sell"
    assert report["trade_history"][-1]["side"] == "sell"
    assert report["positions"] == []
    assert report["notifications"][-2] == "SELL AAPL at 108.0 (TRAILING STOP)"
    assert report["notifications"][-1] == report["summary"]

