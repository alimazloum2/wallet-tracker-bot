# 🪙 Multi-Chain Crypto Wallet Tracker & Generator Bot

A powerful Telegram bot for tracking cryptocurrency wallet balances and generating secure multi-chain wallets across multiple blockchains with real-time USD/CAD price conversion.

[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/your_bot)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Features

### 💼 Wallet Tracking
- ✅ **Multi-Chain Support** - Track wallets on ETH, BSC, SOL, and BTC
- ✅ **Real-Time Balances** - Fetch live balance data from blockchain APIs
- ✅ **Price Conversion** - USD/CAD conversion with live market prices
- ✅ **Portfolio Overview** - Total portfolio value calculation across all chains
- ✅ **Multi-User Support** - Each user has their own wallet list
- ✅ **Persistent Storage** - Your wallets are saved between sessions
- ✅ **Balance Caching** - Shows last known balance if API temporarily fails
- ✅ **Retry Logic** - Automatic retry with exponential backoff for reliability

### 🔐 Wallet Generation
- ✅ **Single-Mnemonic Multi-Chain** - Generate wallets for all 4 chains from one seed phrase
- ✅ **BIP39 Standard** - Industry-standard 12 or 24-word mnemonic phrases
- ✅ **BIP44/BIP84 Derivation** - Proper hierarchical deterministic key derivation
- ✅ **SLIP-0010 for Solana** - ED25519 derivation compatible with Phantom & Solflare
- ✅ **Secure Entropy** - Cryptographically secure random number generation
- ✅ **Wallet Restoration** - Restore existing wallets from mnemonic
- ✅ **Multiple Accounts** - Generate multiple wallets from the same seed
- ✅ **Format Validation** - Validate addresses and mnemonics before use
- ✅ **Auto-Delete Security** - Sensitive info auto-deleted after confirmation

---

## 🌐 Supported Blockchains

| Blockchain | API Provider | API Key Required | Address Format |
|------------|--------------|------------------|----------------|
| **Bitcoin (BTC)** | Blockchain.com | ❌ No | Native SegWit (bc1...) |
| **Ethereum (ETH)** | Etherscan | ✅ Yes | 0x... (42 chars) |
| **Binance Smart Chain (BSC)** | Ankr RPC | ❌ No | 0x... (42 chars) |
| **Solana (SOL)** | Solana RPC / Solscan | ⚠️ Optional | Base58 (32-44 chars) |

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/alimazloum2/wallet-tracker-bot.git
cd wallet-tracker-bot
```

### 2️⃣ Checkout the Latest Branch
```bash
git checkout claude/complete-fix-with-all-files-011CV35MZgyhkd1fp1R4T1rQ
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key
SOLSCAN_API_KEY=your_solscan_api_key  # Optional
```

**Note:** BSC and BTC don't require API keys! 🎉

### 5️⃣ Run the Bot
```bash
python main.py
```

---

## 🔑 Getting API Keys

### Telegram Bot Token (Required)
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Choose a name and username for your bot
4. Copy the token provided

### Etherscan API Key (Required for ETH)
1. Visit [etherscan.io](https://etherscan.io/)
2. Create a free account
3. Navigate to **API-KEYs** section
4. Click **Add** to create a new API key
5. Copy the key to your `.env` file

### Solscan API Key (Optional for SOL)
1. Visit [solscan.io](https://solscan.io/)
2. Contact their support for API access
3. Alternatively, bot works with public Solana RPC

---

## 🤖 Bot Commands

### Wallet Tracking
| Command | Description |
|---------|-------------|
| `/start` | Welcome message and feature overview |
| `/add` | Add a new wallet address to track |
| `/list` | View all your tracked wallets |
| `/balance` | Check balances with current prices |
| `/remove` | Remove a wallet from tracking |
| `/currency` | Switch between USD/CAD |
| `/help` | Show detailed help information |

### Wallet Generation
| Command | Description |
|---------|-------------|
| `/generate` | Generate new secure wallets (ETH, BSC, SOL, BTC) |

---

## 🔐 Wallet Generation Guide

### Via Telegram Bot

1. Send `/generate` to the bot
2. Choose blockchain:
   - **Single Chain** (BTC, ETH, BSC, or SOL)
   - **Multi-Chain** (all 4 at once)
3. ✍️ **Write down your mnemonic on paper**
4. Confirm you've written it down
5. 🗑️ Message auto-deletes for security

### Via Python Script

```python
from wallet_generator import generate_multi_chain_wallet, restore_from_mnemonic

# Generate new multi-chain wallet
wallet = generate_multi_chain_wallet(word_count=12)

print(f"Mnemonic: {wallet['mnemonic']}")
print(f"ETH Address: {wallet['wallets']['eth']['address']}")
print(f"BSC Address: {wallet['wallets']['bsc']['address']}")
print(f"SOL Address: {wallet['wallets']['sol']['address']}")
print(f"BTC Address: {wallet['wallets']['btc']['address']}")

# Restore wallet from existing mnemonic
restored = restore_from_mnemonic("your twelve word mnemonic phrase here")
```

### Test Wallet Generation
```bash
python test_wallet_generator.py
```

---

## 🛤️ Derivation Paths

| Blockchain | Standard | Derivation Path | Curve |
|------------|----------|-----------------|-------|
| **Ethereum (ETH)** | BIP44 | `m/44'/60'/0'/0/0` | secp256k1 |
| **BSC** | BIP44 | `m/44'/60'/0'/0/0` | secp256k1 |
| **Solana (SOL)** | SLIP-0010 | `m/44'/501'/0'/0'` | ed25519 |
| **Bitcoin (BTC)** | BIP84 | `m/84'/0'/0'/0/0` | secp256k1 |

### ✨ Important: Solana ED25519 Derivation

This bot uses **SLIP-0010** standard for Solana key derivation, ensuring **100% compatibility** with:
- ✅ Phantom Wallet
- ✅ Solflare Wallet
- ✅ Ledger Hardware Wallets
- ✅ All standard Solana wallets

Previous versions used incorrect BIP32 derivation which caused wallet inconsistencies. **This has been fixed!**

---

## 📂 Project Structure

```
wallet-tracker-bot/
├── main.py                    # Telegram bot entry point
├── apis.py                    # Blockchain API integrations
├── wallet_tracker.py          # Wallet management & storage
├── price_service.py           # Price fetching & conversion
├── wallet_generator.py        # Multi-chain wallet generator
├── test_wallet_generator.py   # Test suite for wallet generation
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## ⚠️ Security Best Practices

### 🔒 Critical Security Warnings

1. **NEVER share your mnemonic phrase** - Anyone with your mnemonic can steal all your funds
2. **Write mnemonic on paper** - Don't save digitally (no screenshots, no cloud, no notes apps)
3. **Store securely** - Keep paper backup in a safe, fireproof location
4. **Test with small amounts first** - Verify everything works before transferring large amounts
5. **Never commit secrets** - `.env` and `wallets.json` are gitignored for your protection
6. **Use hardware wallets for large amounts** - Software wallets are convenient but less secure

### 🛡️ What This Bot Does

- ✅ **Auto-deletes** sensitive wallet info after you confirm you've written it down
- ✅ **Local storage only** - Private keys never leave your machine
- ✅ **Environment variables** - API keys stored in `.env` (not in code)
- ✅ **Gitignore protection** - Sensitive files excluded from version control

### 🚨 What You Should Do

- ⚠️ **Rotate API keys regularly** - Especially if you suspect compromise
- ⚠️ **Don't run on shared servers** - Only run on machines you control
- ⚠️ **Keep software updated** - Update dependencies regularly for security patches
- ⚠️ **Review code before running** - This is open source - audit it yourself!

---

## 🧪 Testing

### Run Wallet Generator Tests
```bash
python test_wallet_generator.py
```

### Test Generated Wallets
1. Generate a wallet using `/generate`
2. Import mnemonic into Phantom (for SOL)
3. Import mnemonic into MetaMask (for ETH/BSC)
4. Import mnemonic into Electrum (for BTC)
5. Verify addresses match!

---

## 🐛 Troubleshooting

### Common Issues

**"Module not found" error**
```bash
pip install -r requirements.txt --upgrade
```

**"403 Forbidden" from BSC API**
- Don't worry! The bot retries 3 times with delays
- Shows cached balance if all retries fail

**"Invalid mnemonic" error**
- Check spelling carefully
- Ensure 12 or 24 words
- Use English words only

**Solana wallet doesn't match Phantom**
- Make sure you're on the latest branch
- The SLIP-0010 fix ensures compatibility

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

### v2.0.0 - 2025-11-12
- 🔧 **CRITICAL FIX:** Implemented proper SLIP-0010 ED25519 derivation for Solana
- ✅ Solana wallets now compatible with Phantom, Solflare, and all standard wallets
- ✅ Fixed dependency conflict (coincurve 18.0.0)
- ✅ Added .gitignore for Python cache files

### v1.0.0 - 2025-11-09
- 🎉 Initial release
- ✅ Multi-chain wallet tracking (ETH, BSC, SOL, BTC)
- ✅ Wallet generation with BIP39/BIP44
- ✅ Telegram bot integration
- ✅ Price conversion (USD/CAD)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [web3.py](https://github.com/ethereum/web3.py) - Ethereum integration
- [solders](https://github.com/kevinheavey/solders) - Solana Python SDK
- [mnemonic](https://github.com/trezor/python-mnemonic) - BIP39 implementation

---

## 💬 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/alimazloum2/wallet-tracker-bot/issues)
- 💡 **Feature Requests:** Open an issue with the `enhancement` label
- 📧 **Contact:** Open an issue for questions

---

## ⚖️ Disclaimer

This software is provided "as is", without warranty of any kind. Use at your own risk. The developers are not responsible for any loss of funds or damages resulting from the use of this bot. Always test with small amounts and verify addresses before sending large transactions.

**Not financial advice.** Always do your own research (DYOR) before investing in cryptocurrency.

---

Made with ❤️ by the crypto community
