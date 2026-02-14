---
name: simmer-x402
displayName: x402 Payments
description: Make x402 payments to access paid APIs and gated content. Use when a skill needs to fetch data from x402-gated endpoints (like Kaito mindshare API, Simmer premium endpoints, or any x402 provider). Handles 402 Payment Required responses automatically using USDC on Base.
metadata: {"clawdbot":{"emoji":"💳","requires":{"env":["EVM_PRIVATE_KEY"]},"cron":null,"autostart":false}}
authors:
  - Simmer (@simmer_markets)
version: "1.0.0"
---

# x402 Payments

Pay for x402-gated APIs using USDC on Base. This skill enables agents to autonomously make crypto payments when accessing paid web resources.

## When to Use This Skill

Use this skill when:
- A skill or agent needs to fetch data from an x402-gated API (e.g., Kaito mindshare)
- You encounter HTTP 402 Payment Required responses
- You need to check your Base wallet balance (USDC + ETH)
- You want to pay for Simmer premium endpoints beyond free tier rate limits

## Setup

1. **Set your wallet private key**
   ```bash
   export EVM_PRIVATE_KEY=0x...your_private_key...
   ```
   This is the same wallet you use for Polymarket trading. Your EVM address works on all chains — Polygon for trading, Base for x402 payments.

2. **Fund with USDC on Base**
   - Send USDC to your wallet address on Base network
   - A small amount of ETH on Base is needed for gas (~0.001 ETH)
   - x402 payments are gasless for buyers in most cases (facilitator sponsors gas)

3. **Install dependencies**
   ```bash
   pip install x402[httpx,evm]
   ```

## Quick Commands

| Command | Description |
|---------|-------------|
| `python x402_cli.py balance` | Check USDC and ETH balances on Base |
| `python x402_cli.py fetch <url>` | Fetch URL with automatic x402 payment |
| `python x402_cli.py fetch <url> --json` | Same but output raw JSON only |
| `python x402_cli.py fetch <url> --dry-run` | Show payment info without paying |
| `python x402_cli.py fetch <url> --max 5.00` | Override max payment limit |

## Examples

### Check balance
```bash
python x402_cli.py balance
```
```
x402 Wallet Balance
====================
Address: 0x1234...5678
Network: Base Mainnet

USDC:  $42.50
ETH:   0.0051 ETH
```

### Fetch free endpoint (no payment needed)
```bash
python x402_cli.py fetch "https://api.kaito.ai/api/v1/tokens" --json
```

### Fetch paid endpoint (auto-pays via x402)
```bash
python x402_cli.py fetch "https://api.kaito.ai/api/payg/mindshare?token=BTC" --json
```
```
Paid $0.60 USDC via x402
{"mindshare": {"2026-01-16": 0.15, "2026-01-17": 0.14, ...}}
```

### Fetch Simmer premium endpoint
```bash
python x402_cli.py fetch "https://x402.simmer.markets/api/sdk/context/market-123" \
  --header "Authorization: Bearer sk_live_..." --json
```

## Configuration

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Wallet key | `EVM_PRIVATE_KEY` | (required) | Hex-encoded private key |
| Max payment | `X402_MAX_PAYMENT_USD` | 10.00 | Safety cap per request |
| Network | `X402_NETWORK` | mainnet | `mainnet` or `testnet` |

Or set via `config.json` in the skill directory:
```json
{
  "max_payment_usd": 10.00,
  "network": "mainnet"
}
```

## How It Works

1. Skill makes HTTP request to the target URL
2. If server returns 200 — done, no payment needed
3. If server returns 402 Payment Required — x402 SDK reads payment requirements
4. SDK signs a USDC transfer authorization on Base (no gas needed)
5. SDK retries request with payment signature
6. Server verifies payment, returns gated content

All payment handling is automatic via the official Coinbase x402 Python SDK.

## For Other Skills

Other skills can import x402 functions directly:

```python
from skills.x402.x402_cli import x402_fetch

# Returns parsed JSON response
data = await x402_fetch("https://api.kaito.ai/api/payg/mindshare?token=BTC")
```

## Security

- Uses the official Coinbase `x402` Python SDK for payment signing
- Private key never leaves your machine
- Max payment safety cap prevents accidental overspend
- Dry-run mode to preview payments before executing

## Troubleshooting

**"EVM_PRIVATE_KEY not set"**
- Set your wallet private key: `export EVM_PRIVATE_KEY=0x...`

**"Insufficient USDC balance"**
- Fund your wallet with USDC on Base network
- Run `python x402_cli.py balance` to check

**"Payment exceeds max limit"**
- Increase limit: `--max 50` or set `X402_MAX_PAYMENT_USD=50`

**"Unsupported network in payment options"**
- Some providers offer Solana payment options. This skill filters to Base-only automatically.
