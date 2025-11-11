# Crypto Wallet Tracker Bot

A Telegram bot for tracking cryptocurrency wallet balances across multiple blockchains with real-time USD/CAD price conversion.

## Supported Blockchains

- **Bitcoin (BTC)** - via BlockCypher API (no API key needed)
- **Ethereum (ETH)** - via Etherscan API
- **Binance Smart Chain (BSC)** - via Ankr RPC endpoint (no API key needed, with retry logic)
- **Solana (SOL)** - via Solana RPC & Solscan API

## Features

### Wallet Tracking
- ✅ Track multiple wallets across different blockchains
- ✅ Real-time balance fetching
- ✅ USD/CAD price conversion
- ✅ Total portfolio value calculation
- ✅ User-friendly Telegram interface
- ✅ Multi-user support
- ✅ Persistent wallet storage
- ✅ **Retry logic with exponential backoff** for BSC (3 attempts: 0s, 2s, 4s delays)
- ✅ **Balance caching** - shows last known balance if API fails

### Wallet Generation (NEW!)
- ✅ **Multi-chain wallet generator** - Generate wallets for all 4 chains from a single mnemonic
- ✅ **BIP39 mnemonic support** - 12 or 24-word seed phrases
- ✅ **BIP44 derivation** - Industry-standard key derivation
- ✅ **Secure entropy** - Cryptographically secure random generation
- ✅ **Wallet restoration** - Restore wallets from existing mnemonic
- ✅ **Multiple wallets** - Generate multiple accounts from same mnemonic
- ✅ **Format validation** - Validate addresses and mnemonics

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/alimazloum2/wallet-tracker-bot.git
cd wallet-tracker-bot
git checkout claude/add-bitcoin-support-011CV1Ct8yMAtqrqffNir3Jk
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key  # OPTIONAL - not needed anymore
SOLSCAN_API_KEY=your_solscan_api_key
```

**Note:**
- **Bitcoin** uses BlockCypher API - no API key needed!
- **BSC** now uses Ankr RPC endpoint - no API key needed!

### 4. Run the bot
```bash
python main.py
```

## Getting API Keys

### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions
4. Copy the token

### Etherscan API Key
1. Go to [etherscan.io](https://etherscan.io/)
2. Create an account
3. Go to API-KEYs section
4. Create a new API key

### BSCScan API Key (Not Required)
**No longer needed!** BSC now uses Ankr RPC endpoint which is free and doesn't require an API key.

BSCScan deprecated their V2 API, so we switched to a more reliable Ankr RPC endpoint with:
- 3 retry attempts with exponential backoff (0s, 2s, 4s)
- Balance caching for reliability

### Solscan API Key (Optional)
1. Go to [solscan.io](https://solscan.io/)
2. Contact support for API access

## Bot Commands

- `/start` - Welcome message and overview
- `/add` - Add a new wallet to track
- `/list` - View all tracked wallets
- `/balance` - Check balances with fiat values
- `/remove` - Remove a wallet
- `/currency` - Change currency preference (USD/CAD)
- `/help` - Show help information

## Wallet Generation

The project includes a powerful multi-chain wallet generator that creates wallets for all 4 supported blockchains from a single BIP39 mnemonic.

### Quick Start

```python
from wallet_generator import generate_multi_chain_wallet, restore_from_mnemonic

# Generate a new wallet
wallet = generate_multi_chain_wallet(word_count=12)

print(f"Mnemonic: {wallet['mnemonic']}")
print(f"ETH Address: {wallet['wallets']['eth']['address']}")
print(f"BTC Address: {wallet['wallets']['btc']['address']}")
print(f"SOL Address: {wallet['wallets']['sol']['address']}")
print(f"BSC Address: {wallet['wallets']['bsc']['address']}")

# Restore from existing mnemonic
restored = restore_from_mnemonic("your twelve word mnemonic phrase here")
```

### Run Tests

```bash
python test_wallet_generator.py
```

### Key Features

**BIP39 Mnemonic Generation:**
- 12-word or 24-word seed phrases
- 256 bits of cryptographic entropy
- Standard English wordlist

**BIP44/BIP84 Derivation Paths:**
- ETH: `m/44'/60'/0'/0/0`
- BSC: `m/44'/60'/0'/0/0` (EVM compatible)
- SOL: `m/44'/501'/0'/0'`
- BTC: `m/84'/0'/0'/0/0` (Native SegWit)

**Multiple Wallets:**
Generate multiple accounts from same mnemonic using different derivation indices:
```python
wallet1 = generate_multi_chain_wallet(derivation_index=0)
wallet2 = generate_multi_chain_wallet(derivation_index=1)
wallet3 = generate_multi_chain_wallet(derivation_index=2)
```

**Security Notes:**
- ⚠️ **NEVER share your mnemonic or private keys**
- ⚠️ Store mnemonic in a secure location (hardware wallet recommended)
- ⚠️ Loss of mnemonic = loss of funds
- ⚠️ Test with small amounts first
- ⚠️ Never commit mnemonics to version control

### Address Formats

- **ETH/BSC**: `0x` prefixed hex addresses (42 characters)
- **SOL**: Base58 encoded addresses (32-44 characters)
- **BTC**: Native SegWit (Bech32) addresses starting with `bc1` (42-62 characters)

## Project Structure

```
wallet-tracker-bot/
├── main.py                   # Telegram bot entry point
├── apis.py                   # Blockchain API integrations
├── wallet_tracker.py         # Wallet management
├── price_service.py          # Price fetching & conversion
├── wallet_generator.py       # Multi-chain wallet generator (NEW!)
├── test_wallet_generator.py  # Wallet generator test suite (NEW!)
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## License

MIT License
