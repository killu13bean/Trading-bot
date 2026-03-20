from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.engine import TradingEngine


class StaticMarketDataProvider:
    """A minimal static provider for demo purposes."""

    def get_watchlist(self, settings):
        return ["AAPL", "TSLA"]

    def get_current_price(self, symbol: str) -> float:
        sample = {"AAPL": 200.0, "TSLA": 700.0}
        return sample.get(symbol, 0.0)

    def get_historical(self, symbol: str, days: int):
        # simple deterministic synthetic history required for scan
        base = 100 if symbol == "AAPL" else 600
        return [{"close": float(base + i), "volume": 1_000_000 + i * 1000} for i in range(days)]


app = FastAPI(title="Automated Market Scanner")


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    settings = {"watchlist": ["AAPL", "TSLA"], "starting_cash": 100000}
    provider = StaticMarketDataProvider()
    engine = TradingEngine(settings=settings, market_data_provider=provider)
    report = engine.run_cycle()

    summary = report.get("summary", "")
    balance = report.get("balance", 0)
    positions = report.get("positions", [])
    notifications = report.get("notifications", [])
    decisions = report.get("decisions", [])
    scan_results = report.get("scan_results", [])

    def action_color(action: str) -> str:
        normalized = (action or "").lower()
        if "buy" in normalized:
            return "#4CAF50"
        if "sell" in normalized:
            return "#F44336"
        return "#CCCCCC"

    notifications_html = "".join(
        f"<li style='padding:6px 8px;border-bottom:1px solid #333;'>{n}</li>" for n in notifications
    )

    decisions_html = "".join(
        """<li style='padding:10px 12px;border-bottom:1px solid #333;'>
            <strong>{symbol}</strong> - 
            <span style='color:{color};font-weight:600'>{action}</span><br>
            <small>Reason: {reason}</small><br>
            <small>Score: {score}</small>
        </li>""".format(
            symbol=d.get("symbol", "N/A"),
            action=d.get("action", "hold"),
            reason=d.get("reason", "-"),
            score=d.get("score", "-") if d.get("score") is not None else "-",
            color=action_color(d.get("action", "")),
        ) for d in decisions
    )

    scan_html = "".join(
        """<li style='padding:10px 12px;border-bottom:1px solid #333;'>
            <strong>{symbol}</strong><br>
            <span>Price: ${price:.2f}</span> • 
            <span>Trend: {trend_state}</span> • 
            <span>Score: {score}</span>
        </li>""".format(
            symbol=r.get("symbol", "N/A"),
            price=r.get("price", 0.0),
            trend_state=r.get("trend_state", "unknown"),
            score=r.get("score", "-"),
        ) for r in scan_results
    )

    html = f"""
    <html lang='en'>
      <head>
        <meta charset='UTF-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' />
        <title>Automated Market Scanner</title>
        <style>
          body {{ background:#090B10; color:#EEE; font-family:Arial,Helvetica,sans-serif; margin:0; padding:12px; }}
          .container {{ max-width:1100px; margin:0 auto; }}
          .card {{ background:#171F2A; border:1px solid #2C3540; border-radius:12px; padding:14px; box-shadow:0 0 12px rgba(0,0,0,.35); }}
          .header-card {{ padding:16px 14px; }}
          .panel-list {{ list-style:none; padding:0; margin:0; }}
          .panel-list li {{ padding:10px; border-bottom:1px solid #333; }}
          .panel-list li:last-child {{ border-bottom:none; }}
          .label {{ font-weight:700; }}
          .buy {{ color:#4CAF50; }}
          .sell {{ color:#F44336; }}
          .neutral {{ color:#CCCCCC; }}
          @media (max-width: 768px) {{
            body {{ padding:10px; }}
            h1 {{ font-size:1.5rem; }}
            h2 {{ font-size:1.05rem; }}
            .grid {{ display:block; }}
            .card {{ margin-bottom:12px; }}
          }}
          @media (min-width: 769px) {{
            .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:12px; }}
          }}
        </style>
      </head>
      <body>

        <div class='container'>
          <header class='card header-card'>
            <h1 style='margin:0;color:#FFFFFF;'>Automated Market Scanner</h1>
            <p style='margin:8px 0 0;color:#BBB;'>Paper trading dashboard with production-style scanner output.</p>
          </header>

          <section class='grid'>
            <article class='card'>
              <h2 style='margin:0 0 10px;font-size:1.15rem;color:#AFCB6E;'>Summary</h2>
              <p style='margin:0;color:#DDD;line-height:1.5;'>{summary}</p>
            </article>
            <article class='card'>
              <h2 style='margin:0 0 10px;font-size:1.15rem;color:#81C7D4;'>Account</h2>
              <p style='margin:4px 0;color:#EEE;'>Available balance: <strong>${balance:,.2f}</strong></p>
              <p style='margin:4px 0;color:#EEE;'>Open positions: <strong>{len(positions)}</strong></p>
              <p style='margin:4px 0;color:#EEE;'>Notifications: <strong>{len(notifications)}</strong></p>
            </article>
            <article class='card'>
              <h2 style='margin:0 0 10px;font-size:1.15rem;color:#E2C46F;'>Notifications</h2>
              <ul class='panel-list' style='max-height:180px; overflow:auto;'>{notifications_html}</ul>
            </article>
          </section>

          <section style='margin-top:16px;'>
            <h2 style='margin:0 0 8px;font-size:1.2rem;color:#E7E7E7;'>Decisions</h2>
            <div class='card'>
              <ul class='panel-list'>{decisions_html or "<li>No decisions this cycle.</li>"}</ul>
            </div>
          </section>

          <section style='margin-top:16px; margin-bottom:20px;'>
            <h2 style='margin:0 0 8px;font-size:1.2rem;color:#E7E7E7;'>Scan Results</h2>
            <div class='card'>
              <ul class='panel-list'>{scan_html or "<li>No scan results available.</li>"}</ul>
            </div>
          </section>

        </div>

      </body>
    </html>
    """

    return HTMLResponse(content=html)
