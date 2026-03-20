from src.services.reporter import Reporter


def test_reporter_build_cycle_summary():
    reporter = Reporter()
    report = {
        "balance": 99995.0,
        "positions": [{"symbol": "AAPL", "quantity": 1}],
        "decisions": [
            {"action": "buy"},
            {"action": "ignore"},
            {"action": "ignore"},
        ],
        "notifications": ["BUY AAPL at 100.0"],
    }

    summary = reporter.build_cycle_summary(report)
    assert summary == "Cycle Summary | Balance: 99995.00 | Positions: 1 | Buy: 1 Hold: 0 Sell: 0 Ignore: 2 | Notifications: 1"
