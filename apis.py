"""
Blockchain API integration module.
Provides functions to fetch wallet balances from various blockchain explorers.
"""

import requests
import logging
from typing import Dict, Optional
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BlockchainAPIError(Exception):
    """Custom exception for blockchain API errors."""
    pass


def get_eth_balance(address: str) -> Dict[str, any]:
    """
    Fetch Ethereum balance from Etherscan API.

    Args:
        address: Ethereum wallet address

    Returns:
        Dictionary containing balance information:
        {
            'balance': float,
            'balance_wei': str,
            'address': str,
            'blockchain': str
        }

    Raises:
        BlockchainAPIError: If the API request fails
    """
    try:
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': Config.ETHERSCAN_API_KEY
        }

        response = requests.get(Config.ETHERSCAN_API_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') != '1':
            raise BlockchainAPIError(f"Etherscan API error: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_eth = float(balance_wei) / 1e18

        return {
            'balance': balance_eth,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'ETH'
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching ETH balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch ETH balance: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing ETH balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse ETH balance: {str(e)}")


def get_bsc_balance(address: str) -> Dict[str, any]:
    """
    Fetch Binance Smart Chain (BSC) balance from BSCScan API.

    Args:
        address: BSC wallet address

    Returns:
        Dictionary containing balance information:
        {
            'balance': float,
            'balance_wei': str,
            'address': str,
            'blockchain': str
        }

    Raises:
        BlockchainAPIError: If the API request fails
    """
    try:
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': Config.BSCSCAN_API_KEY
        }

        response = requests.get(Config.BSCSCAN_API_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') != '1':
            raise BlockchainAPIError(f"BSCScan API error: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_bnb = float(balance_wei) / 1e18

        return {
            'balance': balance_bnb,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'BSC'
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching BSC balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch BSC balance: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing BSC balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse BSC balance: {str(e)}")


def get_sol_balance(address: str) -> Dict[str, any]:
    """
    Fetch Solana balance from Solscan API.

    Args:
        address: Solana wallet address

    Returns:
        Dictionary containing balance information:
        {
            'balance': float,
            'balance_lamports': int,
            'address': str,
            'blockchain': str
        }

    Raises:
        BlockchainAPIError: If the API request fails
    """
    try:
        url = f"{Config.SOLSCAN_API_URL}/account/{address}"
        headers = {
            'token': Config.SOLSCAN_API_KEY
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get('success', False):
            raise BlockchainAPIError(f"Solscan API error: {data.get('message', 'Unknown error')}")

        balance_lamports = data.get('data', {}).get('lamports', 0)
        balance_sol = float(balance_lamports) / 1e9

        return {
            'balance': balance_sol,
            'balance_lamports': balance_lamports,
            'address': address,
            'blockchain': 'SOL'
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching SOL balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch SOL balance: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing SOL balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse SOL balance: {str(e)}")


def get_balance(address: str, blockchain: str) -> Optional[Dict[str, any]]:
    """
    Fetch balance for a wallet address on a specific blockchain.

    Args:
        address: Wallet address
        blockchain: Blockchain identifier ('ETH', 'BSC', or 'SOL')

    Returns:
        Dictionary containing balance information, or None if fetch fails

    Raises:
        ValueError: If blockchain is not supported
    """
    blockchain = blockchain.upper()

    try:
        if blockchain == 'ETH':
            return get_eth_balance(address)
        elif blockchain == 'BSC':
            return get_bsc_balance(address)
        elif blockchain == 'SOL':
            return get_sol_balance(address)
        else:
            raise ValueError(f"Unsupported blockchain: {blockchain}. Supported: ETH, BSC, SOL")

    except BlockchainAPIError as e:
        logger.error(f"Error fetching balance for {address} on {blockchain}: {e}")
        return None


def validate_address(address: str, blockchain: str) -> bool:
    """
    Validate wallet address format for a specific blockchain.

    Args:
        address: Wallet address to validate
        blockchain: Blockchain identifier ('ETH', 'BSC', or 'SOL')

    Returns:
        True if address format is valid, False otherwise
    """
    blockchain = blockchain.upper()

    if blockchain in ['ETH', 'BSC']:
        # Ethereum and BSC addresses are 42 characters long and start with '0x'
        return len(address) == 42 and address.startswith('0x')
    elif blockchain == 'SOL':
        # Solana addresses are typically 32-44 characters (base58 encoded)
        return 32 <= len(address) <= 44
    else:
        return False
