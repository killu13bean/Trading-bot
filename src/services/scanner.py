from __future__ import annotations

from typing import Any, Dict, List, Mapping, Protocol, Sequence


class MarketDataProvider(Protocol):
    """Protocol for a market data provider used by the scanner."""

    def get_watchlist(self, settings: Mapping[str, Any]) -> Sequence[str]:
        ...

    def get_current_price(self, symbol: str) -> float:
        ...

    def get_historical(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        ...


class Scanner:
    """A simple scanner for paper-trading market signals."""

    def __init__(self, settings: Mapping[str, Any], market_data_provider: MarketDataProvider) -> None:
        """Initialize the scanner.

        Args:
            settings: Dictionary with scanner settings (including optional "watchlist").
            market_data_provider: Provider that supplies price and history data.
        """
        self.settings = settings
        self.market_data_provider = market_data_provider

    def _watchlist(self) -> List[str]:
        """Return watchlist symbols from settings or provider."""
        watchlist = self.settings.get("watchlist")
        if watchlist and isinstance(watchlist, Sequence):
            return list(watchlist)

        try:
            return list(self.market_data_provider.get_watchlist(self.settings))
        except AttributeError:
            return []

    @staticmethod
    def _rolling_sma(values: List[float], period: int) -> float:
        """Compute simple moving average for a list of numeric values."""
        if len(values) < period:
            raise ValueError(f"Not enough data points for SMA period={period}")
        return sum(values[-period:]) / period

    @staticmethod
    def _avg_volume(volumes: List[float], period: int) -> float:
        """Compute average volume over the given period."""
        if len(volumes) < period:
            raise ValueError(f"Not enough data points for avg volume period={period}")
        return sum(volumes[-period:]) / period

    @staticmethod
    def _trend_state(sma_20: float, sma_50: float) -> str:
        """Derive trend state from SMA20 and SMA50."""
        if sma_20 > sma_50:
            return "bullish"
        if sma_20 < sma_50:
            return "bearish"
        return "neutral"

    def scan(self) -> List[Dict[str, Any]]:
        """Run the scan and return computed metrics for each symbol."""
        symbols = self._watchlist()
        results: List[Dict[str, Any]] = []

        for symbol in symbols:
            historical = self.market_data_provider.get_historical(symbol, days=50)

            if not historical or len(historical) < 50:
                # Skip or continue if not enough data
                continue

            close_prices = [float(item["close"]) for item in historical]
            volumes = [float(item["volume"]) for item in historical]

            price = float(self.market_data_provider.get_current_price(symbol))
            sma_20 = self._rolling_sma(close_prices, 20)
            sma_50 = self._rolling_sma(close_prices, 50)
            avg_volume = self._avg_volume(volumes, 20)
            trend_state = self._trend_state(sma_20, sma_50)

            score = 0
            if trend_state == "bullish":
                score += 40
            if price > sma_20:
                score += 30
            if sma_20 > sma_50:
                score += 20
            if avg_volume > 0:
                score += 10
            score = min(score, 100)

            results.append(
                {
                    "symbol": symbol,
                    "price": price,
                    "avg_volume": avg_volume,
                    "sma_20": sma_20,
                    "sma_50": sma_50,
                    "trend_state": trend_state,
                    "score": score,
                }
            )

        results.sort(key=lambda item: item.get("score", 0), reverse=True)
        return results
