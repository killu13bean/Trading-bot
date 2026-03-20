from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Any


@dataclass
class Position:
    symbol: str
    quantity: int
    average_entry_price: float
    stop_loss: float | None = None
    highest_price: float = 0.0
    trailing_stop: float | None = None


@dataclass
class TradeRecord:
    symbol: str
    side: str
    price: float
    quantity: int


class InsufficientCashError(ValueError):
    pass


class InsufficientPositionError(ValueError):
    pass


class PaperBroker:
    """Simple in-memory paper broker for buy/sell simulation."""

    def __init__(self, starting_cash: float) -> None:
        """Initialize broker with starting cash balance."""
        if starting_cash < 0:
            raise ValueError("starting_cash must be non-negative")

        self._cash_balance = float(starting_cash)
        self._positions: Dict[str, Position] = {}
        self._trade_history: List[TradeRecord] = []

    def buy(self, symbol: str, price: float, quantity: int, stop_loss: float | None = None) -> None:
        """Execute a buy trade, updating cash, position, stop-loss, and history."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if price <= 0:
            raise ValueError("price must be positive")
        if stop_loss is not None and stop_loss <= 0:
            raise ValueError("stop_loss must be positive if provided")

        cost = price * quantity
        if cost > self._cash_balance:
            raise InsufficientCashError("Not enough cash to complete buy")

        self._cash_balance -= cost

        existing = self._positions.get(symbol)
        if existing is None:
            self._positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                average_entry_price=price,
                stop_loss=stop_loss,
                highest_price=price,
                trailing_stop=None,
            )
        else:
            total_cost = existing.average_entry_price * existing.quantity + cost
            total_qty = existing.quantity + quantity
            existing.quantity = total_qty
            existing.average_entry_price = total_cost / total_qty
            if stop_loss is not None:
                existing.stop_loss = stop_loss
            if price > existing.highest_price:
                existing.highest_price = price
                existing.trailing_stop = existing.highest_price * 0.92

        self._trade_history.append(TradeRecord(symbol=symbol, side="buy", price=price, quantity=quantity))

    def update_position_price(self, symbol: str, current_price: float) -> None:
        """Update highest price and trailing stop for an existing position."""
        if current_price <= 0:
            raise ValueError("current_price must be positive")

        position = self._positions.get(symbol)
        if position is None:
            raise InsufficientPositionError("No position found for symbol")

        if current_price > position.highest_price:
            position.highest_price = current_price
            position.trailing_stop = current_price * 0.92


    def sell(self, symbol: str, price: float, quantity: int) -> None:
        """Execute a sell trade, updating cash, position, and history."""
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if price <= 0:
            raise ValueError("price must be positive")

        position = self._positions.get(symbol)
        if position is None or position.quantity < quantity:
            raise InsufficientPositionError("Not enough position to complete sell")

        proceeds = price * quantity
        self._cash_balance += proceeds

        position.quantity -= quantity
        if position.quantity == 0:
            del self._positions[symbol]

        self._trade_history.append(TradeRecord(symbol=symbol, side="sell", price=price, quantity=quantity))

    def get_balance(self) -> float:
        """Return current cash balance."""
        return self._cash_balance

    def get_positions(self) -> List[Mapping[str, Any]]:
        """Return copy of current positions as list of dictionaries."""
        return [
            {
                "symbol": p.symbol,
                "quantity": p.quantity,
                "average_entry_price": p.average_entry_price,
                "stop_loss": p.stop_loss,
                "highest_price": p.highest_price,
                "trailing_stop": p.trailing_stop,
            }
            for p in self._positions.values()
        ]

    def get_trade_history(self) -> List[Mapping[str, Any]]:
        """Return copy of trade history records."""
        return [
            {
                "symbol": t.symbol,
                "side": t.side,
                "price": t.price,
                "quantity": t.quantity,
            }
            for t in self._trade_history
        ]
