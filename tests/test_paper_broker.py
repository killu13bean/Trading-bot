import pytest

from src.services.paper_broker import PaperBroker, InsufficientCashError, InsufficientPositionError


def test_successful_buy_updates_balance_and_position():
    broker = PaperBroker(starting_cash=10000)
    broker.buy(symbol="AAPL", price=100, quantity=10)

    assert broker.get_balance() == 10000 - 100 * 10
    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["quantity"] == 10
    assert positions[0]["average_entry_price"] == 100


def test_buy_stores_stop_loss_in_position():
    broker = PaperBroker(starting_cash=10000)
    broker.buy(symbol="AAPL", price=100, quantity=10, stop_loss=95)

    positions = broker.get_positions()
    assert positions[0]["stop_loss"] == 95
    assert positions[0]["highest_price"] == 100
    assert positions[0]["trailing_stop"] is None


def test_update_position_price_adjusts_highest_and_trailing_stop():
    broker = PaperBroker(starting_cash=10000)
    broker.buy(symbol="AAPL", price=100, quantity=10, stop_loss=95)
    broker.update_position_price(symbol="AAPL", current_price=110)

    positions = broker.get_positions()
    assert positions[0]["highest_price"] == 110
    assert positions[0]["trailing_stop"] == 110 * 0.92


def test_successful_sell_updates_balance_and_reduces_position():
    broker = PaperBroker(starting_cash=10000)
    broker.buy(symbol="AAPL", price=100, quantity=10)
    broker.sell(symbol="AAPL", price=110, quantity=5)

    assert broker.get_balance() == 10000 - 1000 + 550
    positions = broker.get_positions()
    assert len(positions) == 1
    assert positions[0]["quantity"] == 5


def test_insufficient_cash_raises_error():
    broker = PaperBroker(starting_cash=500)
    with pytest.raises(InsufficientCashError):
        broker.buy(symbol="AAPL", price=100, quantity=10)


def test_overselling_raises_error():
    broker = PaperBroker(starting_cash=10000)
    broker.buy(symbol="AAPL", price=100, quantity=5)
    with pytest.raises(InsufficientPositionError):
        broker.sell(symbol="AAPL", price=110, quantity=10)
