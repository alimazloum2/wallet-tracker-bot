"""
Configuration module for the Telegram Wallet Tracker Bot.
Loads environment variables and validates required settings.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to store and validate environment variables."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Blockchain Explorer API Keys
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
    SOLSCAN_API_KEY = os.getenv('SOLSCAN_API_KEY')
    BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')

    # API Endpoints (V2)
    ETHERSCAN_API_URL = 'https://api.etherscan.io/v2/api'
    BSCSCAN_API_URL = 'https://api.bscscan.com/v2/api'
    SOLSCAN_API_URL = 'https://public-api.solscan.io'

    @classmethod
    def validate(cls):
        """
        Validate that all required configuration variables are set.

        Raises:
            SystemExit: If any required configuration is missing.
        """
        missing_vars = []

        if not cls.TELEGRAM_BOT_TOKEN:
            missing_vars.append('TELEGRAM_BOT_TOKEN')

        if not cls.ETHERSCAN_API_KEY:
            missing_vars.append('ETHERSCAN_API_KEY')

        if not cls.SOLSCAN_API_KEY:
            missing_vars.append('SOLSCAN_API_KEY')

        if not cls.BSCSCAN_API_KEY:
            missing_vars.append('BSCSCAN_API_KEY')

        if missing_vars:
            print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
            print("Please create a .env file based on .env.example and fill in the required values.")
            sys.exit(1)

    @classmethod
    def get_api_key(cls, blockchain: str) -> str:
        """
        Get the API key for a specific blockchain.

        Args:
            blockchain: The blockchain name ('ETH', 'BSC', or 'SOL')

        Returns:
            The API key for the specified blockchain.

        Raises:
            ValueError: If the blockchain is not supported.
        """
        blockchain = blockchain.upper()

        if blockchain == 'ETH':
            return cls.ETHERSCAN_API_KEY
        elif blockchain == 'BSC':
            return cls.BSCSCAN_API_KEY
        elif blockchain == 'SOL':
            return cls.SOLSCAN_API_KEY
        else:
            raise ValueError(f"Unsupported blockchain: {blockchain}")


# Validate configuration on module import
Config.validate()
