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

        logger.info(f"Fetching ETH balance for address: {address}")
        logger.debug(f"Request URL: {Config.ETHERSCAN_API_URL}")
        logger.debug(f"Request params: {params}")

        response = requests.get(Config.ETHERSCAN_API_URL, params=params, timeout=10)

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        # Check for both status codes: '1' for success and '0' for error
        if data.get('status') == '0':
            error_msg = data.get('message', 'Unknown error')
            result = data.get('result', '')
            logger.error(f"Etherscan API returned error status: {error_msg}, result: {result}")
            raise BlockchainAPIError(f"Etherscan API error: {error_msg} - {result}")

        if data.get('status') != '1':
            logger.error(f"Unexpected Etherscan status: {data.get('status')}, full response: {data}")
            raise BlockchainAPIError(f"Etherscan API unexpected status: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_eth = float(balance_wei) / 1e18

        logger.info(f"Successfully fetched ETH balance: {balance_eth} ETH for {address}")

        return {
            'balance': balance_eth,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'ETH'
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching ETH balance for {address}: {e}")
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

        logger.info(f"Fetching BSC balance for address: {address}")
        logger.debug(f"Request URL: {Config.BSCSCAN_API_URL}")
        logger.debug(f"Request params: {params}")

        response = requests.get(Config.BSCSCAN_API_URL, params=params, timeout=10)

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        # Check for both status codes: '1' for success and '0' for error
        if data.get('status') == '0':
            error_msg = data.get('message', 'Unknown error')
            result = data.get('result', '')
            logger.error(f"BSCScan API returned error status: {error_msg}, result: {result}")
            raise BlockchainAPIError(f"BSCScan API error: {error_msg} - {result}")

        if data.get('status') != '1':
            logger.error(f"Unexpected BSCScan status: {data.get('status')}, full response: {data}")
            raise BlockchainAPIError(f"BSCScan API unexpected status: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_bnb = float(balance_wei) / 1e18

        logger.info(f"Successfully fetched BSC balance: {balance_bnb} BNB for {address}")

        return {
            'balance': balance_bnb,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'BSC'
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching BSC balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch BSC balance: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing BSC balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse BSC balance: {str(e)}")


def get_sol_balance(address: str) -> Dict[str, any]:
    """
    Fetch Solana balance using Solana JSON-RPC API and Solscan API as fallback.

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
    # Method 1: Try Solana RPC API first (most reliable)
    try:
        rpc_url = "https://api.mainnet-beta.solana.com"

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address]
        }

        logger.info(f"Fetching SOL balance for address: {address}")
        logger.debug(f"Request URL: {rpc_url}")
        logger.debug(f"Request payload: {payload}")

        response = requests.post(rpc_url, json=payload, timeout=10)

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        if 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            logger.error(f"Solana RPC API error: {error_msg}")
            raise BlockchainAPIError(f"Solana RPC error: {error_msg}")

        if 'result' not in data or 'value' not in data['result']:
            logger.error(f"Unexpected Solana RPC response: {data}")
            raise BlockchainAPIError("Solana RPC returned unexpected response format")

        balance_lamports = data['result']['value']
        balance_sol = float(balance_lamports) / 1e9

        logger.info(f"Successfully fetched SOL balance: {balance_sol} SOL for {address}")

        return {
            'balance': balance_sol,
            'balance_lamports': balance_lamports,
            'address': address,
            'blockchain': 'SOL'
        }

    except requests.exceptions.RequestException as e:
        logger.warning(f"Solana RPC failed, trying Solscan API: {e}")

        # Method 2: Fallback to Solscan API
        try:
            url = f"{Config.SOLSCAN_API_URL}/account/{address}"
            headers = {
                'token': Config.SOLSCAN_API_KEY,
                'Accept': 'application/json'
            }

            logger.debug(f"Solscan URL: {url}")
            logger.debug(f"Solscan headers: {headers}")

            response = requests.get(url, headers=headers, timeout=10)

            logger.debug(f"Solscan response status: {response.status_code}")
            logger.debug(f"Solscan response: {response.text[:500]}")

            response.raise_for_status()

            data = response.json()

            if not data.get('success', False):
                raise BlockchainAPIError(f"Solscan API error: {data.get('message', 'Unknown error')}")

            balance_lamports = data.get('data', {}).get('lamports', 0)
            balance_sol = float(balance_lamports) / 1e9

            logger.info(f"Successfully fetched SOL balance via Solscan: {balance_sol} SOL for {address}")

            return {
                'balance': balance_sol,
                'balance_lamports': balance_lamports,
                'address': address,
                'blockchain': 'SOL'
            }

        except requests.exceptions.RequestException as e2:
            logger.error(f"Both Solana RPC and Solscan failed for {address}")
            logger.error(f"Solana RPC error: {e}")
            logger.error(f"Solscan error: {e2}")
            raise BlockchainAPIError(f"Failed to fetch SOL balance from both APIs. RPC: {str(e)}, Solscan: {str(e2)}")

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

    logger.info(f"Getting balance for {blockchain} address: {address}")

    # Validate address before making API call
    if not validate_address(address, blockchain):
        logger.error(f"Invalid address format for {blockchain}: {address}")
        return None

    try:
        if blockchain == 'ETH':
            return get_eth_balance(address)
        elif blockchain == 'BSC':
            return get_bsc_balance(address)
        elif blockchain == 'SOL':
            return get_sol_balance(address)
        else:
            logger.error(f"Unsupported blockchain: {blockchain}")
            raise ValueError(f"Unsupported blockchain: {blockchain}. Supported: ETH, BSC, SOL")

    except BlockchainAPIError as e:
        logger.error(f"BlockchainAPIError fetching balance for {address} on {blockchain}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching balance for {address} on {blockchain}: {e}")
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

    logger.debug(f"Validating {blockchain} address: {address}")

    if blockchain in ['ETH', 'BSC']:
        # Ethereum and BSC addresses are 42 characters long and start with '0x'
        is_valid = len(address) == 42 and address.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in address[2:])
        logger.debug(f"ETH/BSC address validation result: {is_valid}")
        return is_valid
    elif blockchain == 'SOL':
        # Solana addresses are typically 32-44 characters (base58 encoded)
        # Base58 alphabet: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
        base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        is_valid = 32 <= len(address) <= 44 and all(c in base58_chars for c in address)
        logger.debug(f"SOL address validation result: {is_valid}")
        return is_valid
    else:
        logger.warning(f"Unknown blockchain for validation: {blockchain}")
        return False
