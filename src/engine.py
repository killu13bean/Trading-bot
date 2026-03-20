from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from src.services.notifier import Notifier
from src.services.paper_broker import PaperBroker
from src.services.reporter import Reporter
from src.services.scanner import Scanner
from src.services.strategy import Strategy


class TradingEngine:
    """Simple trading engine coordinating scanner, strategy, and broker."""

    def __init__(
        self,
        settings: Mapping[str, Any],
        market_data_provider: Any,
        notifier: Optional[Notifier] = None,
        reporter: Optional[Reporter] = None,
        scanner_cls=Scanner,
        strategy_cls=Strategy,
        broker_cls=PaperBroker,
    ) -> None:
        """Initialize engine with settings and injected dependencies."""
        self.settings = dict(settings)
        self.market_data_provider = market_data_provider

        self.scanner = scanner_cls(settings=self.settings, market_data_provider=self.market_data_provider)
        self.strategy = strategy_cls(settings=self.settings)
        start_cash = float(self.settings.get("starting_cash", 100000.0))
        self.broker = broker_cls(starting_cash=start_cash)
        self.notifier = notifier or Notifier()
        self.reporter = reporter or Reporter()

    def run_cycle(self) -> Dict[str, Any]:
        """Run a single scan-strategy-execution cycle and return a report."""
        scan_results = self.scanner.scan()

        broker_positions = self.broker.get_positions()
        # update highest price and trailing stop for owned symbols
        for entry in scan_results:
            symbol = entry.get("symbol")
            price = entry.get("price")
            if isinstance(symbol, str) and isinstance(price, (int, float)):
                owned = next((pos for pos in broker_positions if pos.get("symbol") == symbol), None)
                if owned is not None:
                    self.broker.update_position_price(symbol=symbol, current_price=float(price))

        broker_positions = self.broker.get_positions()
        decisions = self.strategy.evaluate_scan_results(scan_results, broker_positions=broker_positions)

        for decision in decisions:
            action = decision.get("action")
            symbol = decision.get("symbol")
            if not isinstance(symbol, str):
                continue

            price = float(next((s["price"] for s in scan_results if s.get("symbol") == symbol), 0.0))

            if action == "buy":
                stop_loss = price * 0.95
                self.broker.buy(symbol=symbol, price=price, quantity=1, stop_loss=stop_loss)
                self.notifier.notify(f"BUY {symbol} at {price}")
            elif action == "sell":
                # sell full quantity of owned position (V1 behavior)
                current_positions = self.broker.get_positions()
                owned_qty = next((p["quantity"] for p in current_positions if p.get("symbol") == symbol), 0)
                if isinstance(owned_qty, int) and owned_qty > 0:
                    self.broker.sell(symbol=symbol, price=price, quantity=owned_qty)
                    reason = decision.get("reason")
                    if reason == "stop loss hit":
                        self.notifier.notify(f"SELL {symbol} at {price} (STOP LOSS)")
                    elif reason == "trailing stop hit":
                        self.notifier.notify(f"SELL {symbol} at {price} (TRAILING STOP)")
                    else:
                        self.notifier.notify(f"SELL {symbol} at {price}")

        result = {
            "balance": self.broker.get_balance(),
            "positions": self.broker.get_positions(),
            "trade_history": self.broker.get_trade_history(),
            "scan_results": scan_results,
            "decisions": decisions,
            "notifications": [],
        }

        summary = self.reporter.build_cycle_summary(result)
        result["summary"] = summary
        self.notifier.notify(summary)

        result["notifications"] = self.notifier.get_messages()

        return result
