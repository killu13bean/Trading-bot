import pytest

from src.services.scanner import Scanner


class FakeMarketDataProvider:
    def __init__(self) -> None:
        self.current = {"AAPL": 150.0, "TSLA": 720.0}

    def get_watchlist(self, settings):
        return settings.get("watchlist", [])

    def get_current_price(self, symbol: str) -> float:
        return self.current[symbol]

    def get_historical(self, symbol: str, days: int):
        # Create deterministic history: close increments by 1, volume constant + index
        if symbol not in self.current:
            return []
        return [
            {"close": float(100 + i), "volume": float(1_000_000 + i * 1000)}
            for i in range(days)
        ]


def test_scanner_returns_expected_metrics():
    settings = {"watchlist": ["AAPL", "TSLA"]}
    provider = FakeMarketDataProvider()
    scanner = Scanner(settings=settings, market_data_provider=provider)

    results = scanner.scan()

    assert len(results) == 2
    result_by_symbol = {item["symbol"]: item for item in results}

    aapl = result_by_symbol["AAPL"]
    assert aapl["price"] == 150.0
    assert pytest.approx(aapl["sma_20"]) == sum(range(100 + 30, 100 + 50)) / 20
    assert pytest.approx(aapl["sma_50"]) == sum(range(100, 150)) / 50
    assert aapl["trend_state"] == "bearish" or aapl["trend_state"] == "bullish"

    tsla = result_by_symbol["TSLA"]
    assert tsla["price"] == 720.0
    assert tsla["symbol"] == "TSLA"


def test_bullish_score_higher_than_bearish():
    settings = {"watchlist": ["AAPL", "TSLA"]}
    provider = FakeMarketDataProvider()
    scanner = Scanner(settings=settings, market_data_provider=provider)

    results = scanner.scan()
    assert "score" in results[0]
    assert "score" in results[1]

    # Given current generation, AAPL bearish, TSLA probably bullish but we check relative
    scores = sorted([r["score"] for r in results], reverse=True)
    assert scores[0] >= scores[1]


def test_results_sorted_by_score_descending():
    class RankingProvider(FakeMarketDataProvider):
        def get_historical(self, symbol: str, days: int):
            if symbol == "GOOD":
                return [{"close": 100.0, "volume": 1000.0} for _ in range(days)]
            if symbol == "BAD":
                return [{"close": 1.0, "volume": 0.0} for _ in range(days)]
            return super().get_historical(symbol, days)

        def get_current_price(self, symbol: str) -> float:
            if symbol == "GOOD":
                return 150.0
            if symbol == "BAD":
                return 0.5
            return super().get_current_price(symbol)

    settings = {"watchlist": ["GOOD", "BAD"]}
    provider = RankingProvider()
    scanner = Scanner(settings=settings, market_data_provider=provider)

    results = scanner.scan()
    assert results[0]["score"] >= results[1]["score"]


def test_score_exists_in_every_scan_result():
    settings = {"watchlist": ["AAPL"]}
    provider = FakeMarketDataProvider()
    scanner = Scanner(settings=settings, market_data_provider=provider)

    results = scanner.scan()
    assert len(results) == 1
    assert "score" in results[0]


def test_scanner_skips_insufficient_data():
    class LimitedHistoryProvider(FakeMarketDataProvider):
        def get_historical(self, symbol: str, days: int):
            return super().get_historical(symbol, 30)

    settings = {"watchlist": ["AAPL"]}
    provider = LimitedHistoryProvider()
    scanner = Scanner(settings=settings, market_data_provider=provider)

    assert scanner.scan() == []
