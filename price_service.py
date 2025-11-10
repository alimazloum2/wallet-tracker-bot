"""
Price service module for fetching cryptocurrency prices in multiple currencies.
Uses CoinGecko API (free, no API key required).
"""

import requests
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PriceServiceError(Exception):
    """Custom exception for price service errors."""
    pass


# Mapping of blockchain tickers to CoinGecko IDs
COINGECKO_IDS = {
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'BSC': 'binancecoin',  # BSC uses BNB
    'SOL': 'solana'
}


def get_crypto_prices(currencies: list = ['usd', 'cad']) -> Dict[str, Dict[str, float]]:
    """
    Fetch cryptocurrency prices from CoinGecko API.

    Args:
        currencies: List of fiat currencies to fetch prices in (default: ['usd', 'cad'])

    Returns:
        Dictionary mapping crypto symbols to their prices in different currencies:
        {
            'ETH': {'usd': 2500.00, 'cad': 3400.00},
            'BNB': {'usd': 300.00, 'cad': 408.00},
            'SOL': {'usd': 100.00, 'cad': 136.00}
        }

    Raises:
        PriceServiceError: If the API request fails
    """
    try:
        # CoinGecko API endpoint (free, no API key needed)
        url = 'https://api.coingecko.com/api/v3/simple/price'

        # Get unique coin IDs
        coin_ids = ','.join(set(COINGECKO_IDS.values()))
        currencies_str = ','.join(currencies)

        params = {
            'ids': coin_ids,
            'vs_currencies': currencies_str
        }

        logger.info(f"Fetching prices for {coin_ids} in {currencies_str}")

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Convert CoinGecko IDs back to our ticker symbols
        prices = {}
        for symbol, coingecko_id in COINGECKO_IDS.items():
            if coingecko_id in data:
                prices[symbol] = data[coingecko_id]

        logger.info(f"Successfully fetched prices: {prices}")
        return prices

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching crypto prices: {e}")
        raise PriceServiceError(f"Failed to fetch prices: {str(e)}")
    except (ValueError, KeyError) as e:
        logger.error(f"Error parsing price response: {e}")
        raise PriceServiceError(f"Failed to parse prices: {str(e)}")


def get_price_for_currency(crypto_symbol: str, fiat_currency: str) -> Optional[float]:
    """
    Get the price of a specific cryptocurrency in a specific fiat currency.

    Args:
        crypto_symbol: Crypto symbol ('ETH', 'BNB', 'SOL')
        fiat_currency: Fiat currency code ('USD', 'CAD')

    Returns:
        Price as float, or None if unavailable
    """
    try:
        prices = get_crypto_prices([fiat_currency.lower()])

        # Handle BSC (uses BNB price)
        if crypto_symbol == 'BSC':
            crypto_symbol = 'BNB'

        if crypto_symbol in prices and fiat_currency.lower() in prices[crypto_symbol]:
            return prices[crypto_symbol][fiat_currency.lower()]

        return None

    except PriceServiceError as e:
        logger.error(f"Error getting price for {crypto_symbol} in {fiat_currency}: {e}")
        return None


def format_fiat_value(crypto_amount: float, crypto_symbol: str, fiat_currency: str) -> str:
    """
    Format a crypto amount with its fiat value.

    Args:
        crypto_amount: Amount of cryptocurrency
        crypto_symbol: Symbol of the cryptocurrency
        fiat_currency: Fiat currency for conversion

    Returns:
        Formatted string like "0.001000 ETH ($2,500.00 USD)" or "0.001000 ETH (Price unavailable)"
    """
    price = get_price_for_currency(crypto_symbol, fiat_currency)

    if price is None:
        return f"{crypto_amount:.6f} {crypto_symbol} (Price unavailable)"

    fiat_value = crypto_amount * price
    fiat_currency_upper = fiat_currency.upper()

    # Format with currency symbol
    currency_symbols = {'USD': '$', 'CAD': 'CAD $'}
    symbol = currency_symbols.get(fiat_currency_upper, fiat_currency_upper + ' ')

    return f"{crypto_amount:.6f} {crypto_symbol} ({symbol}{fiat_value:,.2f})"


def get_total_value_in_fiat(balances: Dict[str, float], fiat_currency: str) -> Optional[float]:
    """
    Calculate total portfolio value in fiat currency.

    Args:
        balances: Dictionary mapping crypto symbols to amounts {'ETH': 0.5, 'BNB': 10}
        fiat_currency: Fiat currency for conversion

    Returns:
        Total value as float, or None if prices unavailable
    """
    try:
        prices = get_crypto_prices([fiat_currency.lower()])
        total = 0.0

        for symbol, amount in balances.items():
            if amount <= 0:
                continue

            # Handle BSC (uses BNB price)
            price_symbol = 'BNB' if symbol == 'BSC' else symbol

            if price_symbol in prices and fiat_currency.lower() in prices[price_symbol]:
                price = prices[price_symbol][fiat_currency.lower()]
                total += amount * price

        return total

    except PriceServiceError as e:
        logger.error(f"Error calculating total value: {e}")
        return None
