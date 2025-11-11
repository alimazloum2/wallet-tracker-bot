"""
Price service module for fetching cryptocurrency prices in multiple currencies.
Uses CoinGecko API (free, no API key required) with DefiLlama as backup.
Implements caching to reduce API calls and avoid rate limiting.
"""

import requests
import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

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

# DefiLlama coin slugs
DEFILLAMA_SLUGS = {
    'ETH': 'coingecko:ethereum',
    'BNB': 'coingecko:binancecoin',
    'BSC': 'coingecko:binancecoin',
    'SOL': 'coingecko:solana'
}

# Global price cache
_price_cache = {
    'timestamp': None,
    'prices': {},
    'lock': False
}

# Cache duration: 5 minutes
CACHE_DURATION_SECONDS = 300


def _is_cache_valid() -> bool:
    """Check if the price cache is still valid (less than 5 minutes old)."""
    if _price_cache['timestamp'] is None or not _price_cache['prices']:
        return False

    age = datetime.now() - _price_cache['timestamp']
    return age.total_seconds() < CACHE_DURATION_SECONDS


def _fetch_from_coingecko(currencies: list, max_retries: int = 3) -> Dict[str, Dict[str, float]]:
    """
    Fetch prices from CoinGecko API with retry logic.

    Args:
        currencies: List of fiat currencies
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary of prices

    Raises:
        PriceServiceError: If all attempts fail
    """
    url = 'https://api.coingecko.com/api/v3/simple/price'
    coin_ids = ','.join(set(COINGECKO_IDS.values()))
    currencies_str = ','.join(currencies)

    params = {
        'ids': coin_ids,
        'vs_currencies': currencies_str
    }

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[CoinGecko] Attempt {attempt}/{max_retries}: Fetching prices for {coin_ids}")

            # Add delay between attempts (exponential backoff)
            if attempt > 1:
                wait_time = 2 ** (attempt - 1)  # 2, 4, 8 seconds
                logger.info(f"[CoinGecko] Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                # Add small delay even on first attempt to avoid rate limiting
                time.sleep(1)

            response = requests.get(url, params=params, timeout=10)

            # Handle rate limiting (429)
            if response.status_code == 429:
                logger.warning(f"[CoinGecko] Rate limited (429), attempt {attempt}/{max_retries}")
                if attempt < max_retries:
                    continue
                else:
                    raise PriceServiceError("CoinGecko rate limit exceeded")

            response.raise_for_status()
            data = response.json()

            # Convert CoinGecko IDs back to our ticker symbols
            prices = {}
            for symbol, coingecko_id in COINGECKO_IDS.items():
                if coingecko_id in data:
                    prices[symbol] = data[coingecko_id]

            logger.info(f"[CoinGecko] Successfully fetched prices: {prices}")
            return prices

        except requests.exceptions.RequestException as e:
            logger.error(f"[CoinGecko] Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                raise PriceServiceError(f"CoinGecko failed after {max_retries} attempts: {str(e)}")

    raise PriceServiceError("Failed to fetch prices from CoinGecko")


def _fetch_from_defillama(currencies: list) -> Dict[str, Dict[str, float]]:
    """
    Fetch prices from DefiLlama API as backup.

    Args:
        currencies: List of fiat currencies

    Returns:
        Dictionary of prices

    Raises:
        PriceServiceError: If fetch fails
    """
    try:
        logger.info("[DefiLlama] Fetching prices as backup...")
        time.sleep(1)  # Rate limiting

        # DefiLlama uses different format - fetch current prices
        coins = ','.join(set(DEFILLAMA_SLUGS.values()))
        url = f'https://coins.llama.fi/prices/current/{coins}'

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'coins' not in data:
            raise PriceServiceError("Invalid DefiLlama response format")

        # Convert to our format
        prices = {}
        for symbol, slug in DEFILLAMA_SLUGS.items():
            if slug in data['coins']:
                coin_data = data['coins'][slug]
                # DefiLlama returns USD price by default
                usd_price = coin_data.get('price', 0)

                # Build price dict for requested currencies
                price_dict = {}
                for currency in currencies:
                    if currency == 'usd':
                        price_dict['usd'] = usd_price
                    elif currency == 'cad':
                        # Approximate CAD conversion (1 USD ≈ 1.36 CAD)
                        price_dict['cad'] = usd_price * 1.36

                if symbol not in prices:
                    prices[symbol] = price_dict

        logger.info(f"[DefiLlama] Successfully fetched prices: {prices}")
        return prices

    except Exception as e:
        logger.error(f"[DefiLlama] Failed to fetch prices: {e}")
        raise PriceServiceError(f"DefiLlama failed: {str(e)}")


def get_crypto_prices(currencies: list = ['usd', 'cad'], use_cache: bool = True) -> Dict[str, Dict[str, float]]:
    """
    Fetch cryptocurrency prices with caching and fallback mechanisms.

    Args:
        currencies: List of fiat currencies to fetch prices in (default: ['usd', 'cad'])
        use_cache: Whether to use cached prices if available (default: True)

    Returns:
        Dictionary mapping crypto symbols to their prices in different currencies:
        {
            'ETH': {'usd': 2500.00, 'cad': 3400.00},
            'BNB': {'usd': 300.00, 'cad': 408.00},
            'SOL': {'usd': 100.00, 'cad': 136.00}
        }

    Raises:
        PriceServiceError: If all API attempts fail and no cache available
    """
    global _price_cache

    # Check cache first
    if use_cache and _is_cache_valid():
        logger.info(f"[Cache] Using cached prices (age: {(datetime.now() - _price_cache['timestamp']).total_seconds():.0f}s)")
        return _price_cache['prices']

    # Avoid concurrent API calls
    if _price_cache['lock']:
        logger.info("[Cache] Another request is fetching prices, waiting...")
        time.sleep(2)
        if _is_cache_valid():
            return _price_cache['prices']

    _price_cache['lock'] = True

    try:
        # Try CoinGecko first
        try:
            prices = _fetch_from_coingecko(currencies)

            # Update cache
            _price_cache['timestamp'] = datetime.now()
            _price_cache['prices'] = prices
            _price_cache['lock'] = False

            return prices

        except PriceServiceError as e:
            logger.warning(f"[CoinGecko] Failed, trying DefiLlama: {e}")

            # Try DefiLlama as backup
            try:
                prices = _fetch_from_defillama(currencies)

                # Update cache
                _price_cache['timestamp'] = datetime.now()
                _price_cache['prices'] = prices
                _price_cache['lock'] = False

                return prices

            except PriceServiceError as e2:
                logger.error(f"[DefiLlama] Also failed: {e2}")

                # If we have old cache, use it
                if _price_cache['prices']:
                    logger.warning("[Cache] Using stale cache as fallback")
                    _price_cache['lock'] = False
                    return _price_cache['prices']

                _price_cache['lock'] = False
                raise PriceServiceError(f"All price sources failed. CoinGecko: {e}, DefiLlama: {e2}")

    except Exception as e:
        _price_cache['lock'] = False
        logger.error(f"Unexpected error in get_crypto_prices: {e}")

        # Return stale cache if available
        if _price_cache['prices']:
            logger.warning("[Cache] Using stale cache due to unexpected error")
            return _price_cache['prices']

        raise PriceServiceError(f"Failed to fetch prices: {str(e)}")


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
        Formatted string like "0.001000 ETH ($2,500.00 USD)" or "0.001000 ETH" if price unavailable
    """
    price = get_price_for_currency(crypto_symbol, fiat_currency)

    if price is None:
        # Just show the crypto amount without mentioning unavailable price
        return f"{crypto_amount:.6f} {crypto_symbol}"

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
