# Trade Journal Skill - Build Context

## Overview

Build a skill that automatically logs every trade with context, then generates calibration reports to improve trading performance.

## Why This Skill

From user research (Polymarket traders using Moltbot):
> "Every trade records: Entry thesis + probability estimate, Market conditions at entry, Position size vs Kelly optimal, Outcome vs expected value. Monthly mistake report identifies: Calibration errors, Process breaks, Information gaps, Execution failures."

This is a **meta-skill** that makes all other skills better by tracking what works.

## Skill Pattern

**Trigger:** After any trade executes (hook into SDK trade confirmations)
**Action:** Log trade context to persistent storage
**Output:** On-demand reports and periodic summaries

## Core Features

### 1. Trade Logging
For every trade, capture:
```json
{
  "trade_id": "uuid",
  "timestamp": "ISO8601",
  "market_id": "polymarket-id",
  "market_question": "Will X happen?",
  "side": "yes|no",
  "action": "buy|sell",
  "shares": 10.5,
  "price": 0.65,
  "cost_usd": 6.83,
  
  "context": {
    "source": "copytrading|signalsniper|weather|manual",
    "thesis": "Whale 0x123 entered, news signal bullish",
    "confidence": 0.75,
    "market_price_at_entry": 0.65,
    "simmer_ai_price": 0.70,
    "resolution_date": "2025-02-15",
    "time_to_resolution_hours": 168
  },
  
  "outcome": {
    "resolved": false,
    "resolution_price": null,
    "pnl_usd": null,
    "pnl_pct": null,
    "was_correct": null
  }
}
```

### 2. Outcome Tracking
- Poll resolved markets periodically
- Update `outcome` fields when market resolves
- Calculate actual P&L vs expected

### 3. Reports

**On-demand:**
```bash
python tradejournal.py --report daily
python tradejournal.py --report weekly
python tradejournal.py --report monthly
```

**Report includes:**
- Win rate overall + by skill source
- Calibration curve (confidence vs actual win rate)
- Biggest winners/losers
- Common mistake patterns
- Skill performance comparison

### 4. Calibration Analysis
Compare stated confidence to actual outcomes:
```
Confidence 90%+ trades: 4/5 correct (80% actual) → Overconfident
Confidence 60-70% trades: 8/10 correct (80% actual) → Underconfident
```

## File Structure

```
skills/tradejournal/
├── README.md (SKILL.md content)
├── SKILL.md
├── tradejournal.py          # Main script
├── scripts/
│   └── status.py            # Quick status check
└── data/                    # Local storage (gitignored)
    └── trades.json          # Trade log
```

## Dependencies

- Simmer SDK (SIMMER_API_KEY)
- Local JSON storage (or SQLite for scale)
- No external APIs needed

## CLI Interface

```bash
# Log a trade manually (usually auto-logged)
python tradejournal.py --log --market "abc123" --side yes --shares 10 --price 0.65 --thesis "News signal"

# View recent trades
python tradejournal.py --history 10

# Generate report
python tradejournal.py --report weekly

# Update outcomes for resolved markets
python tradejournal.py --sync-outcomes

# Show calibration analysis
python tradejournal.py --calibration

# Export to CSV
python tradejournal.py --export trades.csv
```

## Integration Points

### With Existing Skills

Other skills should call the journal after trading:
```python
# In copytrading_trader.py after successful trade:
from tradejournal import log_trade

log_trade(
    trade_id=result['trade_id'],
    market_id=market_id,
    source="copytrading",
    thesis=f"Mirroring whale {wallet[:10]}",
    confidence=0.70
)
```

### With Simmer API

Use existing endpoints:
- `GET /api/sdk/positions` - current positions
- `GET /api/sdk/trades` - trade history (if available)
- Market resolution status from market data

## Storage Design

Simple JSON file for MVP:
```json
{
  "trades": [...],
  "metadata": {
    "created_at": "...",
    "last_sync": "...",
    "total_trades": 50
  }
}
```

Later: Could move to SQLite for better querying.

## Cron Suggestion

```yaml
metadata: {"clawdbot":{"emoji":"📓","requires":{"env":["SIMMER_API_KEY"]},"cron":"0 0 * * *"}}
```
Daily at midnight - sync outcomes and generate summary.

## Success Metrics

1. Every trade logged with context
2. Calibration report shows over/under confidence patterns
3. Users can identify which skills perform best
4. Mistake patterns become visible

## Implementation Order

1. Basic trade logging (JSON storage)
2. CLI for history/reports
3. Outcome syncing (poll resolved markets)
4. Calibration analysis
5. Integration hooks for other skills

## Questions to Resolve

1. Should journal pull from Simmer trade history API or rely on skills calling it?
2. How to handle trades made outside of skills (manual dashboard trades)?
3. Should reports be pushed to Telegram/Discord or just CLI?

---

## Ready to Build

Start with `tradejournal.py` - the core logging and reporting script.

Reference existing skills for patterns:
- `/tmp/simmer-sdk/skills/copytrading/copytrading_trader.py`
- `/tmp/simmer-sdk/skills/signalsniper/signal_sniper.py`
- `/tmp/simmer-sdk/skills/weather/weather_trader.py`

Simmer API docs: Check `/tmp/simmer/scripts/local_dev_server.py` for endpoints.
