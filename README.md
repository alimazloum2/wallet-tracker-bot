# Telegram Wallet Tracker Bot

A production-ready Telegram bot that tracks cryptocurrency wallet balances across multiple blockchains including Ethereum, Binance Smart Chain, and Solana.

## Features

- **Multi-Blockchain Support**: Track wallets on Ethereum (ETH), Binance Smart Chain (BSC), and Solana (SOL)
- **Real-Time Balance Tracking**: Fetch current balances using blockchain explorer APIs
- **User-Friendly Interface**: Interactive Telegram bot with inline keyboards
- **Persistent Storage**: Wallet data is saved and persists between bot restarts
- **Error Handling**: Robust error handling and validation
- **Custom Labels**: Add custom labels to identify your wallets
- **Multi-Wallet Support**: Track unlimited wallets across different blockchains

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))
- API Keys:
  - Etherscan API Key ([Get it here](https://etherscan.io/apis))
  - BSCScan API Key ([Get it here](https://bscscan.com/apis))
  - Solscan API Key ([Get it here](https://public-api.solscan.io/))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/wallet-tracker-bot.git
cd wallet-tracker-bot
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file based on the `.env.example` template:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
SOLSCAN_API_KEY=your_solscan_api_key_here
BSCSCAN_API_KEY=your_bscscan_api_key_here
```

### 5. Run the Bot

```bash
python main.py
```

## Usage

### Bot Commands

- `/start` - Welcome message and bot introduction
- `/help` - Display help information and available commands
- `/add` - Add a new wallet to track
- `/list` - List all your tracked wallets
- `/balance` - Check current balances for all wallets
- `/remove` - Remove a wallet from tracking

### Adding a Wallet

1. Send `/add` to the bot
2. Enter the wallet address
3. Select the blockchain (ETH, BSC, or SOL)
4. Enter a label (or type 'skip' for default)
5. Wallet is added and ready to track!

### Checking Balances

1. Send `/balance` to the bot
2. The bot will fetch real-time balances for all your tracked wallets
3. View individual wallet balances and total balance per blockchain

## Project Structure

```
wallet-tracker-bot/
├── main.py              # Bot entry point and command handlers
├── wallet_tracker.py    # WalletTracker class for managing wallets
├── apis.py              # Blockchain API integration functions
├── config.py            # Configuration and environment variable loading
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── wallets.json        # Wallet data storage (created automatically)
```

## Architecture

### Components

1. **main.py**: Telegram bot interface
   - Command handlers for user interactions
   - Conversation flow for adding wallets
   - Inline keyboard menus

2. **wallet_tracker.py**: Wallet management
   - Add/remove wallets
   - Persistent JSON storage
   - Balance aggregation

3. **apis.py**: Blockchain API integration
   - Etherscan API for Ethereum (V2 endpoint)
   - BSCScan API for Binance Smart Chain
   - Solana JSON-RPC API (primary) with Solscan fallback
   - Enhanced address validation with Base58 checking
   - Comprehensive error handling with detailed logging
   - Automatic fallback mechanisms

4. **config.py**: Configuration management
   - Environment variable loading
   - API endpoint configuration
   - Configuration validation

## API Endpoints Used

- **Etherscan**: `https://api.etherscan.io/api` (V2 API with proper error handling)
- **BSCScan**: `https://api.bscscan.com/api` (V2 API with proper error handling)
- **Solana RPC**: `https://api.mainnet-beta.solana.com` (Primary - JSON-RPC 2.0)
- **Solscan**: `https://public-api.solscan.io` (Fallback for Solana)

### API Features

- **Detailed Logging**: All API calls are logged with request/response details for debugging
- **Error Status Handling**: Properly handles both '0' (error) and '1' (success) status codes from Etherscan/BSCScan
- **Dual Solana Support**: Uses reliable Solana RPC API as primary, with Solscan as fallback
- **Address Validation**: Validates address format before making API calls (hex for ETH/BSC, Base58 for SOL)
- **Timeout Protection**: All API calls have 10-second timeout to prevent hanging

## Error Handling

The bot includes comprehensive error handling for:
- Invalid wallet addresses
- API request failures
- Network timeouts
- Missing configuration
- Invalid user input

## Security Considerations

- Never commit your `.env` file (it's in `.gitignore`)
- Keep your API keys secure
- Regularly rotate API keys
- Monitor API usage to prevent rate limiting
- The bot does not have access to private keys (read-only)

## Limitations

- API rate limits apply based on your API key tier
- Free tier API keys may have usage restrictions
- Balance fetching requires active internet connection
- Wallet addresses are validated by format only (not ownership)

## Troubleshooting

### Bot doesn't start
- Verify all environment variables are set correctly in `.env`
- Check that the Telegram bot token is valid
- Ensure Python 3.8+ is installed

### Balance fetching fails
- Verify API keys are correct and active
- Check API rate limits haven't been exceeded
- Ensure wallet addresses are valid for the selected blockchain

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using the virtual environment

## Development

### Running in Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run with debug logging
python main.py
```

### Adding New Blockchains

To add support for a new blockchain:

1. Add the API configuration to `config.py`
2. Implement the balance fetching function in `apis.py`
3. Update address validation in `apis.py`
4. Add the blockchain option to the bot interface in `main.py`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for informational purposes only. Always verify balances on official blockchain explorers. The developers are not responsible for any financial decisions made based on this bot's data.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: your-email@example.com

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [web3.py](https://github.com/ethereum/web3.py) - Ethereum interaction library
- Etherscan, BSCScan, and Solscan for their APIs

## Roadmap

- [ ] Add price conversion (USD, EUR, etc.)
- [ ] Support for ERC-20 tokens
- [ ] Transaction history tracking
- [ ] Price alerts and notifications
- [ ] Portfolio analytics
- [ ] Export wallet data
- [ ] Multi-language support

---

**Made with ❤️ for the crypto community**
