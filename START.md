START
  │
  ▼
Load Settings
- Market selected: stocks / crypto / both
- Mode selected: investment / trading / both
- Paper trading ON
- Notification system ON
  │
  ▼
Build Scan Universe
- US stocks watchlist
- Crypto watchlist
- Remove low-volume / bad-liquidity assets
  │
  ▼
Fetch Market Data
- Price
- Volume
- Trend data
- Indicators
- Support / resistance
  │
  ▼
Run Scanner Engine
  │
  ├── Check Trend
  ├── Check Momentum
  ├── Check Volume
  ├── Check Structure
  ├── Check Risk/Reward
  └── Give Score out of 100
  │
  ▼
Classify Asset
  │
  ├── Score too low → IGNORE
  ├── Score medium → WATCHLIST
  ├── Score high + investment conditions met → INVESTMENT CANDIDATE
  └── Score high + trading conditions met → TRADING CANDIDATE
  │
  ▼
Decision Engine
  │
  ├── If no position exists:
  │      ├── Buy
  │      └── Wait
  │
  └── If position already exists:
         ├── Hold
         ├── Tighten stop
         ├── Partial sell
         └── Full sell
  │
  ▼
Paper Broker Engine
  │
  ├── Execute paper buy
  ├── Execute paper sell
  ├── Update balance
  ├── Update open positions
  └── Store trade history
  │
  ▼
Position Manager
  │
  ├── Track entry price
  ├── Track current price
  ├── Track highest price reached
  ├── Track stop loss
  ├── Track trailing stop
  ├── Track take-profit zones
  └── Re-check all open positions every cycle
  │
  ▼
Exit Engine
  │
  ├── Hard stop hit? → SELL
  ├── Trailing stop hit? → SELL
  ├── Profit target hit? → Partial sell or tighten stop
  ├── Trend breaking? → SELL
  ├── Momentum weakening? → Tighten stop / Partial sell / SELL
  └── Market condition weak? → Reduce risk / SELL
  │
  ▼
Notification Engine
  │
  ├── Buy alert
  ├── Sell alert
  ├── Hold update
  ├── Top opportunities today
  ├── Daily summary
  └── Weekly summary
  │
  ▼
Dashboard Update
- Open positions
- Closed trades
- Watchlist
- Top opportunities
- P&L
- Alerts history
  │
  ▼
Repeat Next Cycle