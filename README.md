# Blofin BTCUSDT Grid Trading Bot

A professional grid trading bot for Blofin exchange targeting BTCUSDT perpetual futures.
Designed for $1,000 accounts with 3-5x leverage. Uses limit (maker) orders exclusively for minimum fees (0.02%).

## Features
- Limit-only orders (0.02% maker fee vs 0.06% taker)
- Auto grid rebalancing when price breaks range
- Stop-loss protection
- Live PnL and trade tracking
- Demo mode for safe testing
- Fully configurable via environment variables

## Setup

1. Clone the repo:
   git clone https://github.com/nashk0619-a11y/blofin-grid-bot.git
   cd blofin-grid-bot

2. Install dependencies:
   pip install -r requirements.txt

3. Copy env file and add your credentials:
   cp .env.example .env

4. Run in demo mode first:
   python grid_bot.py

## Configuration

| Variable | Default | Description |
|---|---|---|
| BLOFIN_MODE | demo | 'demo' or 'live' |
| SYMBOL | BTC-USDT | Trading pair |
| TOTAL_CAPITAL | 800 | USDT to allocate |
| LEVERAGE | 3 | Leverage multiplier |
| GRID_LEVELS | 25 | Number of grid lines |
| GRID_RANGE_PCT | 15 | +/- % range from entry |
| STOP_LOSS_PCT | 20 | Stop loss % from entry |

## Recommended Settings for $1,000 Account

- Capital: $800 (keep $200 as margin buffer)
- Leverage: 3x (conservative)
- Grid Levels: 25
- Range: +/-15%
- Stop Loss: -20%

## Risk Warning

Trading cryptocurrency futures involves significant risk of loss.
Past performance does not guarantee future results.
Always test in demo mode before going live.
