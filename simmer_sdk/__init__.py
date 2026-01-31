"""
Simmer SDK - Python client for Simmer prediction markets

Usage:
    from simmer_sdk import SimmerClient

    client = SimmerClient(api_key="sk_live_...")

    # List markets
    markets = client.get_markets(import_source="polymarket")

    # Execute trade (server-side signing with Simmer-managed wallet)
    result = client.trade(market_id="...", side="yes", amount=10.0)

    # Get positions
    positions = client.get_positions()

External Wallet Trading:
    # Trade with your own Polymarket wallet (local signing)
    client = SimmerClient(
        api_key="sk_live_...",
        venue="polymarket",
        private_key="0x..."  # Your wallet's private key
    )

    # Link wallet to your account (one-time setup)
    client.link_wallet()

    # Check approvals
    approvals = client.check_approvals()

    # If missing approvals, get transaction data
    if not approvals["all_set"]:
        from simmer_sdk.approvals import get_missing_approval_transactions
        txs = get_missing_approval_transactions(approvals)
        # Sign and send each tx from your wallet

    # Trade (signs locally, submits through Simmer)
    result = client.trade(market_id="...", side="yes", amount=10.0)

    SECURITY WARNING:
    - Never log or print your private key
    - Never commit it to version control
    - Use environment variables or secure secret management
"""

from .client import SimmerClient
from .approvals import (
    get_required_approvals,
    get_approval_transactions,
    get_missing_approval_transactions,
    format_approval_guide,
)

__version__ = "0.2.6"
__all__ = [
    "SimmerClient",
    "get_required_approvals",
    "get_approval_transactions",
    "get_missing_approval_transactions",
    "format_approval_guide",
]
