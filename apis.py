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
        # Debug: Show API key status
        api_key = Config.ETHERSCAN_API_KEY
        api_key_preview = f"{api_key[:5]}..." if api_key and len(api_key) > 5 else "NOT_SET"

        print(f"\n{'='*60}")
        print(f"[ETHERSCAN DEBUG] Fetching balance for: {address}")
        print(f"[ETHERSCAN DEBUG] API Key: {api_key_preview}")
        print(f"[ETHERSCAN DEBUG] API URL: {Config.ETHERSCAN_API_URL}")

        params = {
            'chainid': '1',  # Ethereum mainnet
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': api_key
        }

        # Build full URL for debugging
        param_str = '&'.join([f"{k}={v}" for k, v in params.items() if k != 'apikey'])
        full_url = f"{Config.ETHERSCAN_API_URL}?{param_str}&apikey={api_key_preview}"
        print(f"[ETHERSCAN DEBUG] Full URL: {full_url}")

        logger.info(f"Fetching ETH balance for address: {address}")
        logger.debug(f"Request URL: {Config.ETHERSCAN_API_URL}")
        logger.debug(f"Request params: {params}")

        response = requests.get(Config.ETHERSCAN_API_URL, params=params, timeout=10)

        print(f"[ETHERSCAN DEBUG] Response Status: {response.status_code}")
        print(f"[ETHERSCAN DEBUG] Response Headers: {dict(response.headers)}")
        print(f"[ETHERSCAN DEBUG] Response Body: {response.text}")

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        print(f"[ETHERSCAN DEBUG] Parsed JSON: {data}")

        # Check for both status codes: '1' for success and '0' for error
        if data.get('status') == '0':
            error_msg = data.get('message', 'Unknown error')
            result = data.get('result', '')
            print(f"[ETHERSCAN ERROR] Status='0': {error_msg} - {result}")
            logger.error(f"Etherscan API returned error status: {error_msg}, result: {result}")
            raise BlockchainAPIError(f"Etherscan API error: {error_msg} - {result}")

        if data.get('status') != '1':
            print(f"[ETHERSCAN ERROR] Unexpected status: {data.get('status')}")
            logger.error(f"Unexpected Etherscan status: {data.get('status')}, full response: {data}")
            raise BlockchainAPIError(f"Etherscan API unexpected status: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_eth = float(balance_wei) / 1e18

        print(f"[ETHERSCAN SUCCESS] Balance: {balance_eth} ETH ({balance_wei} wei)")
        print(f"{'='*60}\n")

        logger.info(f"Successfully fetched ETH balance: {balance_eth} ETH for {address}")

        return {
            'balance': balance_eth,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'ETH'
        }

    except requests.exceptions.RequestException as e:
        print(f"[ETHERSCAN ERROR] Network error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Network error fetching ETH balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch ETH balance: {str(e)}")
    except (ValueError, KeyError) as e:
        print(f"[ETHERSCAN ERROR] Parse error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Error parsing ETH balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse ETH balance: {str(e)}")
    except Exception as e:
        print(f"[ETHERSCAN ERROR] Unexpected error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Unexpected error in get_eth_balance: {e}")
        raise BlockchainAPIError(f"Unexpected error: {str(e)}")


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
        # Debug: Show API key status
        api_key = Config.BSCSCAN_API_KEY
        api_key_preview = f"{api_key[:5]}..." if api_key and len(api_key) > 5 else "NOT_SET"

        print(f"\n{'='*60}")
        print(f"[BSCSCAN DEBUG] Fetching balance for: {address}")
        print(f"[BSCSCAN DEBUG] API Key: {api_key_preview}")
        print(f"[BSCSCAN DEBUG] API URL: {Config.BSCSCAN_API_URL}")

        params = {
            'chainid': '56',  # BSC mainnet
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': api_key
        }

        # Build full URL for debugging
        param_str = '&'.join([f"{k}={v}" for k, v in params.items() if k != 'apikey'])
        full_url = f"{Config.BSCSCAN_API_URL}?{param_str}&apikey={api_key_preview}"
        print(f"[BSCSCAN DEBUG] Full URL: {full_url}")

        logger.info(f"Fetching BSC balance for address: {address}")
        logger.debug(f"Request URL: {Config.BSCSCAN_API_URL}")
        logger.debug(f"Request params: {params}")

        response = requests.get(Config.BSCSCAN_API_URL, params=params, timeout=10)

        print(f"[BSCSCAN DEBUG] Response Status: {response.status_code}")
        print(f"[BSCSCAN DEBUG] Response Body: {response.text[:500]}")

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        print(f"[BSCSCAN DEBUG] Parsed JSON: {data}")

        # Check for both status codes: '1' for success and '0' for error
        if data.get('status') == '0':
            error_msg = data.get('message', 'Unknown error')
            result = data.get('result', '')
            print(f"[BSCSCAN ERROR] Status='0': {error_msg} - {result}")
            logger.error(f"BSCScan API returned error status: {error_msg}, result: {result}")
            raise BlockchainAPIError(f"BSCScan API error: {error_msg} - {result}")

        if data.get('status') != '1':
            print(f"[BSCSCAN ERROR] Unexpected status: {data.get('status')}")
            logger.error(f"Unexpected BSCScan status: {data.get('status')}, full response: {data}")
            raise BlockchainAPIError(f"BSCScan API unexpected status: {data.get('message', 'Unknown error')}")

        balance_wei = data.get('result', '0')
        balance_bnb = float(balance_wei) / 1e18

        print(f"[BSCSCAN SUCCESS] Balance: {balance_bnb} BNB ({balance_wei} wei)")
        print(f"{'='*60}\n")

        logger.info(f"Successfully fetched BSC balance: {balance_bnb} BNB for {address}")

        return {
            'balance': balance_bnb,
            'balance_wei': balance_wei,
            'address': address,
            'blockchain': 'BSC'
        }

    except requests.exceptions.RequestException as e:
        print(f"[BSCSCAN ERROR] Network error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Network error fetching BSC balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch BSC balance: {str(e)}")
    except (ValueError, KeyError) as e:
        print(f"[BSCSCAN ERROR] Parse error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Error parsing BSC balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse BSC balance: {str(e)}")
    except Exception as e:
        print(f"[BSCSCAN ERROR] Unexpected error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Unexpected error in get_bsc_balance: {e}")
        raise BlockchainAPIError(f"Unexpected error: {str(e)}")


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


def get_btc_balance(address: str) -> Dict[str, any]:
    """
    Fetch Bitcoin balance from BlockCypher API.

    Args:
        address: Bitcoin wallet address

    Returns:
        Dictionary containing balance information:
        {
            'balance': float,
            'balance_satoshis': int,
            'address': str,
            'blockchain': str
        }

    Raises:
        BlockchainAPIError: If the API request fails
    """
    try:
        # BlockCypher API (free, no API key required)
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance"

        print(f"\n{'='*60}")
        print(f"[BLOCKCYPHER DEBUG] Fetching balance for: {address}")
        print(f"[BLOCKCYPHER DEBUG] API URL: {url}")

        logger.info(f"Fetching BTC balance for address: {address}")
        logger.debug(f"Request URL: {url}")

        response = requests.get(url, timeout=10)

        print(f"[BLOCKCYPHER DEBUG] Response Status: {response.status_code}")
        print(f"[BLOCKCYPHER DEBUG] Response Body: {response.text}")

        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        print(f"[BLOCKCYPHER DEBUG] Parsed JSON: {data}")

        # Check for error in response
        if 'error' in data:
            error_msg = data.get('error', 'Unknown error')
            print(f"[BLOCKCYPHER ERROR] API error: {error_msg}")
            logger.error(f"BlockCypher API returned error: {error_msg}")
            raise BlockchainAPIError(f"BlockCypher API error: {error_msg}")

        # Get balance in satoshis (1 BTC = 100,000,000 satoshis)
        balance_satoshis = data.get('balance', 0)
        balance_btc = float(balance_satoshis) / 1e8

        print(f"[BLOCKCYPHER SUCCESS] Balance: {balance_btc} BTC ({balance_satoshis} satoshis)")
        print(f"{'='*60}\n")

        logger.info(f"Successfully fetched BTC balance: {balance_btc} BTC for {address}")

        return {
            'balance': balance_btc,
            'balance_satoshis': balance_satoshis,
            'address': address,
            'blockchain': 'BTC'
        }

    except requests.exceptions.RequestException as e:
        print(f"[BLOCKCYPHER ERROR] Network error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Network error fetching BTC balance for {address}: {e}")
        raise BlockchainAPIError(f"Failed to fetch BTC balance: {str(e)}")
    except (ValueError, KeyError) as e:
        print(f"[BLOCKCYPHER ERROR] Parse error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Error parsing BTC balance response: {e}")
        raise BlockchainAPIError(f"Failed to parse BTC balance: {str(e)}")
    except Exception as e:
        print(f"[BLOCKCYPHER ERROR] Unexpected error: {e}")
        print(f"{'='*60}\n")
        logger.error(f"Unexpected error in get_btc_balance: {e}")
        raise BlockchainAPIError(f"Unexpected error: {str(e)}")


def get_balance(address: str, blockchain: str) -> Optional[Dict[str, any]]:
    """
    Fetch balance for a wallet address on a specific blockchain.

    Args:
        address: Wallet address
        blockchain: Blockchain identifier ('ETH', 'BSC', 'SOL', or 'BTC')

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
        elif blockchain == 'BTC':
            return get_btc_balance(address)
        else:
            logger.error(f"Unsupported blockchain: {blockchain}")
            raise ValueError(f"Unsupported blockchain: {blockchain}. Supported: ETH, BSC, SOL, BTC")

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
        blockchain: Blockchain identifier ('ETH', 'BSC', 'SOL', or 'BTC')

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
    elif blockchain == 'BTC':
        # Bitcoin addresses can be:
        # - Legacy (P2PKH): starts with '1', 26-35 characters
        # - P2SH: starts with '3', 26-35 characters
        # - Bech32 (SegWit): starts with 'bc1', 42-62 characters
        # All use Base58 (legacy/P2SH) or Bech32 encoding
        if address.startswith('bc1'):
            # Bech32 addresses (lowercase, alphanumeric except '1', 'b', 'i', 'o')
            bech32_chars = '023456789acdefghjklmnpqrstuvwxyz'
            is_valid = 42 <= len(address) <= 62 and all(c in bech32_chars for c in address.lower())
        elif address.startswith('1') or address.startswith('3'):
            # Legacy and P2SH addresses (Base58)
            base58_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            is_valid = 26 <= len(address) <= 35 and all(c in base58_chars for c in address)
        else:
            is_valid = False
        logger.debug(f"BTC address validation result: {is_valid}")
        return is_valid
    else:
        logger.warning(f"Unknown blockchain for validation: {blockchain}")
        return False
