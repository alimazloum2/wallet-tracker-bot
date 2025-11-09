"""
Wallet Tracker module for managing and tracking cryptocurrency wallets.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from apis import get_balance, validate_address, BlockchainAPIError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class WalletTracker:
    """
    Manages wallet tracking for multiple users across different blockchains.
    """

    def __init__(self, storage_file: str = 'wallets.json'):
        """
        Initialize the WalletTracker.

        Args:
            storage_file: Path to the JSON file for persisting wallet data
        """
        self.storage_file = storage_file
        self.wallets = self._load_wallets()

    def _load_wallets(self) -> Dict:
        """
        Load wallets from storage file.

        Returns:
            Dictionary of user wallets
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading wallets from {self.storage_file}: {e}")
                return {}
        return {}

    def _save_wallets(self) -> bool:
        """
        Save wallets to storage file.

        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.wallets, f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error saving wallets to {self.storage_file}: {e}")
            return False

    def add_wallet(self, user_id: int, address: str, blockchain: str, label: Optional[str] = None) -> Dict[str, any]:
        """
        Add a wallet to track for a user.

        Args:
            user_id: Telegram user ID
            address: Wallet address
            blockchain: Blockchain identifier ('ETH', 'BSC', or 'SOL')
            label: Optional label for the wallet

        Returns:
            Dictionary with status and message

        Raises:
            ValueError: If address format is invalid
        """
        blockchain = blockchain.upper()
        user_id_str = str(user_id)

        # Validate address format
        if not validate_address(address, blockchain):
            raise ValueError(f"Invalid {blockchain} address format")

        # Initialize user's wallet list if not exists
        if user_id_str not in self.wallets:
            self.wallets[user_id_str] = []

        # Check if wallet already exists
        for wallet in self.wallets[user_id_str]:
            if wallet['address'] == address and wallet['blockchain'] == blockchain:
                return {
                    'success': False,
                    'message': f'Wallet already tracked: {address} ({blockchain})'
                }

        # Add wallet
        wallet_data = {
            'address': address,
            'blockchain': blockchain,
            'label': label or f'{blockchain} Wallet',
            'added_at': datetime.now().isoformat()
        }

        self.wallets[user_id_str].append(wallet_data)
        self._save_wallets()

        logger.info(f"Added wallet {address} ({blockchain}) for user {user_id}")

        return {
            'success': True,
            'message': f'Wallet added successfully: {address} ({blockchain})'
        }

    def remove_wallet(self, user_id: int, address: str, blockchain: str) -> Dict[str, any]:
        """
        Remove a wallet from tracking for a user.

        Args:
            user_id: Telegram user ID
            address: Wallet address
            blockchain: Blockchain identifier

        Returns:
            Dictionary with status and message
        """
        blockchain = blockchain.upper()
        user_id_str = str(user_id)

        if user_id_str not in self.wallets:
            return {
                'success': False,
                'message': 'No wallets tracked for this user'
            }

        # Find and remove wallet
        initial_count = len(self.wallets[user_id_str])
        self.wallets[user_id_str] = [
            w for w in self.wallets[user_id_str]
            if not (w['address'] == address and w['blockchain'] == blockchain)
        ]

        if len(self.wallets[user_id_str]) == initial_count:
            return {
                'success': False,
                'message': f'Wallet not found: {address} ({blockchain})'
            }

        self._save_wallets()
        logger.info(f"Removed wallet {address} ({blockchain}) for user {user_id}")

        return {
            'success': True,
            'message': f'Wallet removed successfully: {address} ({blockchain})'
        }

    def get_user_wallets(self, user_id: int) -> List[Dict]:
        """
        Get all wallets tracked for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of wallet dictionaries
        """
        user_id_str = str(user_id)
        return self.wallets.get(user_id_str, [])

    def get_wallet_balance(self, address: str, blockchain: str) -> Optional[Dict[str, any]]:
        """
        Get current balance for a specific wallet.

        Args:
            address: Wallet address
            blockchain: Blockchain identifier

        Returns:
            Balance information dictionary or None if fetch fails
        """
        try:
            balance_data = get_balance(address, blockchain)
            return balance_data
        except Exception as e:
            logger.error(f"Error getting balance for {address} on {blockchain}: {e}")
            return None

    def get_all_balances(self, user_id: int) -> List[Dict[str, any]]:
        """
        Get balances for all wallets tracked by a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of dictionaries containing wallet and balance information
        """
        wallets = self.get_user_wallets(user_id)
        results = []

        for wallet in wallets:
            balance_data = self.get_wallet_balance(wallet['address'], wallet['blockchain'])

            result = {
                'label': wallet['label'],
                'address': wallet['address'],
                'blockchain': wallet['blockchain'],
                'added_at': wallet['added_at']
            }

            if balance_data:
                result['balance'] = balance_data['balance']
                result['status'] = 'success'
            else:
                result['balance'] = None
                result['status'] = 'error'

            results.append(result)

        return results

    def get_total_value(self, user_id: int) -> Dict[str, float]:
        """
        Get total value of all tracked wallets by blockchain.

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with total values per blockchain
        """
        balances = self.get_all_balances(user_id)
        totals = {'ETH': 0.0, 'BSC': 0.0, 'SOL': 0.0}

        for balance in balances:
            if balance['status'] == 'success' and balance['balance'] is not None:
                blockchain = balance['blockchain']
                totals[blockchain] += balance['balance']

        return totals

    def get_wallet_count(self, user_id: int) -> int:
        """
        Get the number of wallets tracked for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            Number of tracked wallets
        """
        return len(self.get_user_wallets(user_id))
