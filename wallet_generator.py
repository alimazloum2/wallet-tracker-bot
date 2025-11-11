"""
Multi-Chain Wallet Generator Module

Generates cryptocurrency wallets for ETH, BSC, SOL, and BTC using:
- BIP39 mnemonic seed phrases (12 words)
- BIP44 derivation paths for each blockchain
- Secure entropy generation

Security: Private keys are sensitive. Store mnemonic safely.
"""

import hashlib
import hmac
import secrets
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

# External dependencies
from mnemonic import Mnemonic
from eth_account import Account
from eth_account.hdaccount import generate_mnemonic as eth_generate_mnemonic, seed_from_mnemonic, key_from_seed, ETHEREUM_DEFAULT_PATH
from solders.keypair import Keypair  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
import base58
from bip32 import BIP32

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# BIP44 Derivation Paths
DERIVATION_PATHS = {
    'ETH': "m/44'/60'/0'/0/0",
    'BSC': "m/44'/60'/0'/0/0",  # Same as ETH (EVM compatible)
    'SOL': "m/44'/501'/0'/0'",
    'BTC': "m/44'/0'/0'/0/0"
}


class WalletGeneratorError(Exception):
    """Custom exception for wallet generation errors."""
    pass


def _derive_key_from_path(seed: bytes, path: str) -> bytes:
    """
    Derive a private key from seed using BIP44 derivation path.
    Uses proper BIP32 implementation.

    Args:
        seed: BIP39 seed bytes
        path: BIP44 derivation path (e.g., "m/44'/60'/0'/0/0")

    Returns:
        32-byte private key
    """
    # Use proper BIP32 library
    bip32 = BIP32.from_seed(seed)
    derived_key = bip32.get_privkey_from_path(path)
    return derived_key


def generate_mnemonic(word_count: int = 12) -> str:
    """
    Generate a BIP39 mnemonic seed phrase.

    Args:
        word_count: Number of words (12 or 24)

    Returns:
        Mnemonic phrase as string

    Raises:
        WalletGeneratorError: If word_count is invalid
    """
    if word_count not in [12, 24]:
        raise WalletGeneratorError("Word count must be 12 or 24")

    # Generate entropy
    # 12 words = 128 bits, 24 words = 256 bits
    entropy_bits = 128 if word_count == 12 else 256
    entropy = secrets.token_bytes(entropy_bits // 8)

    # Create mnemonic
    mnemo = Mnemonic("english")
    mnemonic = mnemo.to_mnemonic(entropy)

    logger.info(f"Generated {word_count}-word mnemonic")
    return mnemonic


def validate_mnemonic(mnemonic: str) -> bool:
    """
    Validate a BIP39 mnemonic phrase.

    Args:
        mnemonic: Mnemonic phrase to validate

    Returns:
        True if valid, False otherwise
    """
    mnemo = Mnemonic("english")
    return mnemo.check(mnemonic)


def generate_eth_wallet(seed: bytes, derivation_index: int = 0) -> Dict[str, str]:
    """
    Generate Ethereum wallet from seed.

    Args:
        seed: BIP39 seed bytes
        derivation_index: Account index for derivation path (default: 0)

    Returns:
        Dictionary with address and private key
    """
    # Modify derivation path with custom index
    path = f"m/44'/60'/0'/0/{derivation_index}"

    # Derive private key
    private_key_bytes = _derive_key_from_path(seed, path)

    # Create account from private key
    account = Account.from_key(private_key_bytes)

    logger.info(f"Generated ETH wallet: {account.address}")

    return {
        'address': account.address,
        'privateKey': account.key.hex(),
        'derivationPath': path
    }


def generate_bsc_wallet(seed: bytes, derivation_index: int = 0) -> Dict[str, str]:
    """
    Generate Binance Smart Chain wallet from seed.
    BSC uses same derivation as Ethereum (EVM compatible).

    Args:
        seed: BIP39 seed bytes
        derivation_index: Account index for derivation path (default: 0)

    Returns:
        Dictionary with address and private key
    """
    # BSC uses same derivation as ETH
    wallet = generate_eth_wallet(seed, derivation_index)
    wallet['derivationPath'] = f"m/44'/60'/0'/0/{derivation_index}"

    logger.info(f"Generated BSC wallet: {wallet['address']}")

    return wallet


def generate_sol_wallet(seed: bytes, derivation_index: int = 0) -> Dict[str, str]:
    """
    Generate Solana wallet from seed.

    Args:
        seed: BIP39 seed bytes
        derivation_index: Account index for derivation path (default: 0)

    Returns:
        Dictionary with address and private key
    """
    # Solana uses different derivation path
    # Note: Solana's derivation is slightly different from standard BIP44
    # For compatibility, we derive a key and use it directly

    path = f"m/44'/501'/{derivation_index}'/0'"
    private_key_bytes = _derive_key_from_path(seed, path)

    # Create Solana keypair from seed
    keypair = Keypair.from_seed(private_key_bytes[:32])

    # Get public key (address)
    address = str(keypair.pubkey())

    # Get private key in base58 format (standard for Solana)
    private_key_bytes_full = bytes(keypair)  # Returns 64 bytes (32 private + 32 public)
    private_key_base58 = base58.b58encode(private_key_bytes_full).decode('utf-8')

    logger.info(f"Generated SOL wallet: {address}")

    return {
        'address': address,
        'privateKey': private_key_base58,
        'derivationPath': path
    }


def generate_btc_wallet(seed: bytes, derivation_index: int = 0) -> Dict[str, str]:
    """
    Generate Bitcoin wallet from seed.
    Creates Legacy (P2PKH) address starting with '1'.

    Args:
        seed: BIP39 seed bytes
        derivation_index: Account index for derivation path (default: 0)

    Returns:
        Dictionary with address and private key
    """
    import hashlib

    path = f"m/44'/0'/0'/0/{derivation_index}"
    private_key_bytes = _derive_key_from_path(seed, path)

    # Create Bitcoin address (Legacy P2PKH format)
    # 1. Get public key from private key using secp256k1
    from coincurve import PublicKey
    public_key = PublicKey.from_secret(private_key_bytes).format(compressed=True)

    # 2. SHA256 hash of public key
    sha256_hash = hashlib.sha256(public_key).digest()

    # 3. RIPEMD160 hash
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # 4. Add version byte (0x00 for mainnet)
    versioned_hash = b'\x00' + ripemd160_hash

    # 5. Double SHA256 for checksum
    checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]

    # 6. Add checksum and encode to base58
    address = base58.b58encode(versioned_hash + checksum).decode('utf-8')

    # Convert private key to hex format (64 characters)
    private_key_hex = private_key_bytes.hex()

    # Convert private key to WIF (Wallet Import Format)
    extended_key = b'\x80' + private_key_bytes + b'\x01'  # 0x80 = mainnet, 0x01 = compressed
    wif_checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    wif = base58.b58encode(extended_key + wif_checksum).decode('utf-8')

    logger.info(f"Generated BTC wallet: {address}")

    return {
        'address': address,
        'privateKey': wif,  # WIF format (most common)
        'privateKeyHex': private_key_hex,  # Hex format (alternative)
        'derivationPath': path
    }


def generate_multi_chain_wallet(word_count: int = 12, derivation_index: int = 0) -> Dict:
    """
    Generate wallets for ETH, BSC, SOL, and BTC from a single mnemonic.

    Args:
        word_count: Number of words for mnemonic (12 or 24)
        derivation_index: Account index for derivation (default: 0)

    Returns:
        Dictionary containing:
        {
            'mnemonic': str,
            'wallets': {
                'eth': {...},
                'bsc': {...},
                'sol': {...},
                'btc': {...}
            },
            'createdAt': str,
            'warning': str
        }

    Raises:
        WalletGeneratorError: If generation fails
    """
    try:
        # Step 1: Generate BIP39 mnemonic
        mnemonic = generate_mnemonic(word_count)

        # Step 2: Create seed from mnemonic (PBKDF2)
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(mnemonic, passphrase="")

        # Step 3 & 4: Derive keys and generate addresses for each chain
        wallets = {
            'eth': generate_eth_wallet(seed, derivation_index),
            'bsc': generate_bsc_wallet(seed, derivation_index),
            'sol': generate_sol_wallet(seed, derivation_index),
            'btc': generate_btc_wallet(seed, derivation_index)
        }

        # Step 5: Return all data in secure format
        result = {
            'mnemonic': mnemonic,
            'wallets': wallets,
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'derivationIndex': derivation_index,
            'warning': '⚠️ CRITICAL: Store mnemonic safely. Never share private keys. Loss of mnemonic = loss of funds.'
        }

        logger.info(f"Successfully generated multi-chain wallet (derivation index: {derivation_index})")
        return result

    except Exception as e:
        logger.error(f"Failed to generate multi-chain wallet: {e}")
        raise WalletGeneratorError(f"Wallet generation failed: {str(e)}")


def restore_from_mnemonic(mnemonic: str, derivation_index: int = 0) -> Dict:
    """
    Restore multi-chain wallet from existing mnemonic.

    Args:
        mnemonic: BIP39 mnemonic phrase
        derivation_index: Account index for derivation (default: 0)

    Returns:
        Same structure as generate_multi_chain_wallet()

    Raises:
        WalletGeneratorError: If mnemonic is invalid or restoration fails
    """
    # Validate mnemonic
    if not validate_mnemonic(mnemonic):
        raise WalletGeneratorError("Invalid mnemonic phrase")

    try:
        # Create seed from mnemonic
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(mnemonic, passphrase="")

        # Generate wallets from seed
        wallets = {
            'eth': generate_eth_wallet(seed, derivation_index),
            'bsc': generate_bsc_wallet(seed, derivation_index),
            'sol': generate_sol_wallet(seed, derivation_index),
            'btc': generate_btc_wallet(seed, derivation_index)
        }

        result = {
            'mnemonic': mnemonic,
            'wallets': wallets,
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'derivationIndex': derivation_index,
            'restored': True,
            'warning': '⚠️ CRITICAL: Store mnemonic safely. Never share private keys. Loss of mnemonic = loss of funds.'
        }

        logger.info(f"Successfully restored multi-chain wallet from mnemonic (derivation index: {derivation_index})")
        return result

    except Exception as e:
        logger.error(f"Failed to restore wallet from mnemonic: {e}")
        raise WalletGeneratorError(f"Wallet restoration failed: {str(e)}")


# Example usage (for testing only - remove in production)
if __name__ == "__main__":
    print("=" * 80)
    print("MULTI-CHAIN WALLET GENERATOR - TEST MODE")
    print("=" * 80)
    print()

    # Generate new wallet
    print("Generating new multi-chain wallet...")
    wallet = generate_multi_chain_wallet(word_count=12)

    print(f"\n{wallet['warning']}")
    print(f"\nMnemonic: {wallet['mnemonic']}")
    print(f"Created: {wallet['createdAt']}")
    print("\nWallets:")

    for chain, data in wallet['wallets'].items():
        print(f"\n{chain.upper()}:")
        print(f"  Address: {data['address']}")
        print(f"  Path: {data['derivationPath']}")
        print(f"  Private Key: {data['privateKey'][:10]}...{data['privateKey'][-10:]} (truncated)")

    print("\n" + "=" * 80)
    print("TEST: Restoring wallet from mnemonic...")
    print("=" * 80)

    # Test restoration
    restored = restore_from_mnemonic(wallet['mnemonic'])

    # Verify addresses match
    print("\nVerification:")
    for chain in ['eth', 'bsc', 'sol', 'btc']:
        match = wallet['wallets'][chain]['address'] == restored['wallets'][chain]['address']
        status = "✓" if match else "✗"
        print(f"{status} {chain.upper()}: {restored['wallets'][chain]['address']}")

    print("\n" + "=" * 80)
