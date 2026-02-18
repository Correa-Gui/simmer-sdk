"""
Solana Transaction Signing Utilities

Signs Solana transactions locally for Kalshi BYOW trading.
Uses solders (Python) for signing — no Node.js required.

SECURITY NOTE: The private key is read from SOLANA_PRIVATE_KEY environment variable
and is NEVER logged or transmitted. All signing happens locally.

Dependencies (included in simmer-sdk):
    solders>=0.27.1   — Solana transaction types and keypair
    base58>=2.1.1     — Base58 encode/decode for Solana keys
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Environment variable for Solana private key
SOLANA_PRIVATE_KEY_ENV_VAR = "SOLANA_PRIVATE_KEY"


def has_solana_key() -> bool:
    """Check if a Solana private key is configured."""
    return bool(os.environ.get(SOLANA_PRIVATE_KEY_ENV_VAR))


def _load_keypair():
    """
    Load a solders Keypair from the SOLANA_PRIVATE_KEY env var.

    Returns:
        solders.keypair.Keypair

    Raises:
        ValueError: If env var is not set or key format is invalid
        ImportError: If solders/base58 are not installed
    """
    raw = os.environ.get(SOLANA_PRIVATE_KEY_ENV_VAR)
    if not raw:
        raise ValueError(
            f"{SOLANA_PRIVATE_KEY_ENV_VAR} environment variable is not set. "
            "Set it to your base58-encoded Solana secret key."
        )

    try:
        import base58 as _base58
        from solders.keypair import Keypair
    except ImportError as e:
        raise ImportError(
            f"Missing dependency for Solana signing: {e}. "
            "Run: pip install simmer-sdk --upgrade"
        ) from e

    try:
        key_bytes = _base58.b58decode(raw.strip())
    except Exception as e:
        raise ValueError(
            f"Invalid {SOLANA_PRIVATE_KEY_ENV_VAR} format — expected base58-encoded secret key: {e}"
        ) from e

    # Solana secret keys are 64 bytes (32-byte seed + 32-byte public key)
    # solders also accepts 32-byte seeds
    try:
        if len(key_bytes) == 64:
            return Keypair.from_bytes(key_bytes)
        elif len(key_bytes) == 32:
            return Keypair.from_seed(key_bytes)
        else:
            raise ValueError(f"Invalid key length: expected 32 or 64 bytes, got {len(key_bytes)}")
    except Exception as e:
        raise ValueError(f"Could not load Solana keypair: {e}") from e


def get_solana_public_key() -> Optional[str]:
    """
    Get the Solana public key (wallet address) from the configured private key.

    Returns:
        Base58-encoded public key string, or None if no key is configured.
    """
    if not has_solana_key():
        return None

    try:
        keypair = _load_keypair()
        return str(keypair.pubkey())
    except Exception as e:
        logger.error("Failed to derive Solana public key: %s", e)
        return None


def sign_solana_transaction(unsigned_tx_base64: str) -> str:
    """
    Sign a Solana transaction using the configured private key.

    The transaction must be a VersionedTransaction serialized to base64.
    This is the format returned by DFlow for Kalshi trades.

    Args:
        unsigned_tx_base64: Base64-encoded unsigned VersionedTransaction

    Returns:
        Base64-encoded signed transaction

    Raises:
        ValueError: If SOLANA_PRIVATE_KEY env var is not set or key is invalid
        RuntimeError: If signing fails

    Example:
        # Get unsigned tx from Simmer API (via DFlow)
        unsigned = api.get_kalshi_quote(market_id, side, amount)

        # Sign locally (called automatically by SimmerClient)
        signed = sign_solana_transaction(unsigned['transaction'])

        # Submit signed tx
        result = api.submit_kalshi_trade(signed_transaction=signed, ...)
    """
    import base64

    try:
        from solders.transaction import VersionedTransaction
    except ImportError as e:
        raise ImportError(
            f"Missing dependency for Solana signing: {e}. "
            "Run: pip install simmer-sdk --upgrade"
        ) from e

    keypair = _load_keypair()

    try:
        tx_bytes = base64.b64decode(unsigned_tx_base64)
    except Exception as e:
        raise ValueError(f"Invalid base64 transaction: {e}") from e

    try:
        tx = VersionedTransaction.from_bytes(tx_bytes)
        tx.sign([keypair], tx.message.recent_blockhash)
        return base64.b64encode(bytes(tx)).decode()
    except Exception as e:
        raise RuntimeError(f"Solana signing failed: {e}") from e


def validate_solana_key() -> bool:
    """
    Validate that the configured Solana key is usable.

    Returns:
        True if the key is valid and can be used for signing.
    """
    if not has_solana_key():
        return False
    try:
        pubkey = get_solana_public_key()
        return pubkey is not None and len(pubkey) > 0
    except Exception:
        return False
