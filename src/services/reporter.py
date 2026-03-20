from __future__ import annotations

from typing import Dict


class Reporter:
    """Builds human-readable cycle summaries from engine reports."""

    def build_cycle_summary(self, report: Dict[str, object]) -> str:
        """Build a short, deterministic summary for a completed cycle."""
        balance = float(report.get("balance", 0.0))
        positions = report.get("positions", [])
        decisions = report.get("decisions", [])
        notifications = report.get("notifications", [])

        buy_count = sum(1 for d in decisions if d.get("action") == "buy")
        hold_count = sum(1 for d in decisions if d.get("action") == "hold")
        sell_count = sum(1 for d in decisions if d.get("action") == "sell")
        ignore_count = sum(1 for d in decisions if d.get("action") == "ignore")

        result = (
            f"Cycle Summary | Balance: {balance:.2f} | Positions: {len(positions)} "
            f"| Buy: {buy_count} Hold: {hold_count} Sell: {sell_count} Ignore: {ignore_count} "
            f"| Notifications: {len(notifications)}"
        )

        return result
