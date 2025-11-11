"""
Configuration module for the Wallet Tracker Bot.
Loads environment variables and provides configuration settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for storing API keys and settings."""

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

    # Blockchain API Keys
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', '')
    BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY', '')
    SOLSCAN_API_KEY = os.getenv('SOLSCAN_API_KEY', '')

    # API URLs
    ETHERSCAN_API_URL = 'https://api.etherscan.io/v2/api'
    BSCSCAN_API_URL = 'https://api.bscscan.com/v2/api'
    SOLSCAN_API_URL = 'https://public-api.solscan.io'

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

        return True
