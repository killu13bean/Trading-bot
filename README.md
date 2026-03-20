# Trading Bot (Paper Trading Market Scanner)

A local paper-trading market scanner with a FastAPI dashboard, stop-loss/trailing-stop support, and a simple decision engine.

## Features

- Market scanning engine using synthetic sample data
- Strategy rules: buy/sell/hold with score thresholds, stop-loss, trailing stop
- Paper broker with position tracking and cash balance
- Notifications and summary report for each cycle
- FastAPI status dashboard (dark mode, cards, decisions/result panels)
- Render deployment compatible

## Quick start

1. Create Python environment (optional)
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests
   ```bash
   python -m pytest -q
   ```
4. Run locally
   ```bash
   set PORT=8000
   uvicorn src.app:app --host 0.0.0.0 --port %PORT%
   ```
5. Open browser: `http://127.0.0.1:8000/`

## GitHub Actions CI

A workflow is included at `.github/workflows/ci.yml` to run tests automatically on push/pull request.

## Render deployment

1. Connect repo: `https://github.com/killu13bean/Trading-bot`
2. Build command:
   ```bash
   pip install -r requirements.txt
   ```
3. Start command:
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port $PORT
   ```

## Notes

- No JavaScript or templates are used (inline CSS only)
- This is a lightweight demo for educational paper trading strategy behavior
