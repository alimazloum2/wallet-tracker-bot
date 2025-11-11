# Crypto Wallet Tracker Bot

A Telegram bot for tracking cryptocurrency wallet balances across multiple blockchains with real-time USD/CAD price conversion.

## Supported Blockchains

- **Bitcoin (BTC)** - via BlockCypher API (no API key needed)
- **Ethereum (ETH)** - via Etherscan API
- **Binance Smart Chain (BSC)** - via Ankr RPC endpoint (no API key needed, with retry logic)
- **Solana (SOL)** - via Solana RPC & Solscan API

## Features

- ✅ Track multiple wallets across different blockchains
- ✅ Real-time balance fetching
- ✅ USD/CAD price conversion
- ✅ Total portfolio value calculation
- ✅ User-friendly Telegram interface
- ✅ Multi-user support
- ✅ Persistent wallet storage
- ✅ **Retry logic with exponential backoff** for BSC (3 attempts: 0s, 2s, 4s delays)
- ✅ **Balance caching** - shows last known balance if API fails

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

## Project Structure

```
wallet-tracker-bot/
├── main.py              # Telegram bot entry point
├── apis.py              # Blockchain API integrations
├── wallet_tracker.py    # Wallet management
├── price_service.py     # Price fetching & conversion
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## License

MIT License
