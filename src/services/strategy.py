from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional


class Strategy:
    """Simple trading strategy evaluator."""

    def __init__(self, settings: Optional[Mapping[str, Any]] = None) -> None:
        """Initialize strategy with optional settings."""
        self.settings = {} if settings is None else dict(settings)

    def evaluate_scan_results(
        self,
        scan_results: List[Mapping[str, Any]],
        broker_positions: Optional[List[Mapping[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Evaluate scan results and return a list of trading decisions."""
        owned = set()
        owned_stop_loss: Dict[str, float] = {}
        owned_trailing_stop: Dict[str, float] = {}
        if broker_positions:
            for pos in broker_positions:
                symbol = pos.get("symbol")
                if isinstance(symbol, str):
                    owned.add(symbol)
                    stop_loss = pos.get("stop_loss")
                    if isinstance(stop_loss, (int, float)):
                        owned_stop_loss[symbol] = float(stop_loss)
                    ts = pos.get("trailing_stop")
                    if isinstance(ts, (int, float)):
                        owned_trailing_stop[symbol] = float(ts)

        decisions: List[Dict[str, Any]] = []

        for entry in scan_results:
            symbol = entry.get("symbol")
            trend_state = entry.get("trend_state")
            price = entry.get("price")
            sma_20 = entry.get("sma_20")
            avg_volume = entry.get("avg_volume")
            score = entry.get("score")

            if not isinstance(symbol, str):
                decisions.append({"symbol": None, "action": "ignore", "reason": "invalid symbol", "score": score})
                continue

            if symbol in owned:
                current_stop_loss = owned_stop_loss.get(symbol)
                current_trailing_stop = owned_trailing_stop.get(symbol)

                if (
                    isinstance(price, (int, float))
                    and isinstance(current_stop_loss, (int, float))
                    and price <= current_stop_loss
                ):
                    decisions.append({"symbol": symbol, "action": "sell", "reason": "stop loss hit", "score": score})
                    continue

                if (
                    isinstance(price, (int, float))
                    and isinstance(current_trailing_stop, (int, float))
                    and price <= current_trailing_stop
                ):
                    decisions.append({"symbol": symbol, "action": "sell", "reason": "trailing stop hit", "score": score})
                    continue

                if trend_state == "bullish":
                    decisions.append({"symbol": symbol, "action": "hold", "reason": "owned and bullish", "score": score})
                    continue
                if trend_state == "bearish":
                    decisions.append({"symbol": symbol, "action": "sell", "reason": "owned and bearish", "score": score})
                    continue
                decisions.append({"symbol": symbol, "action": "ignore", "reason": "owned but not bullish or bearish", "score": score})
                continue

            can_buy = (
                trend_state == "bullish"
                and isinstance(price, (int, float))
                and isinstance(sma_20, (int, float))
                and isinstance(avg_volume, (int, float))
                and isinstance(score, (int, float))
                and price > sma_20
                and avg_volume > 0
                and score >= 70
            )

            if can_buy:
                decisions.append({"symbol": symbol, "action": "buy", "reason": "bullish and above score threshold", "score": score})
            else:
                decisions.append({"symbol": symbol, "action": "ignore", "reason": "does not meet buy conditions", "score": score})

        return decisions
