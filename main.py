"""
Telegram Wallet Tracker Bot - Main Entry Point
A bot to track cryptocurrency wallet balances across multiple blockchains.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from config import Config
from wallet_tracker import WalletTracker
from price_service import format_fiat_value, get_total_value_in_fiat
from wallet_generator import generate_multi_chain_wallet

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize wallet tracker
tracker = WalletTracker()

# Conversation states
WAITING_FOR_ADDRESS, WAITING_FOR_BLOCKCHAIN, WAITING_FOR_LABEL = range(3)
WAITING_FOR_GENERATE_BLOCKCHAIN, WAITING_FOR_READY_CONFIRMATION, WAITING_FOR_WRITTEN_CONFIRMATION, WAITING_FOR_ADD_GENERATED = range(3, 7)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    """
    user = update.effective_user
    user_id = update.effective_user.id
    current_currency = tracker.get_user_currency(user_id)

    welcome_message = f"""
👋 Welcome to Wallet Tracker Bot, {user.first_name}!

I help you track cryptocurrency wallet balances across multiple blockchains.

**Supported Blockchains:**
• Bitcoin (BTC)
• Ethereum (ETH)
• Binance Smart Chain (BSC)
• Solana (SOL)

**Currency Preference:** {current_currency}

**Available Commands:**
/start - Show this welcome message
/generate - Generate a new wallet (BTC, ETH, BSC, or SOL)
/add - Add an existing wallet to track
/list - List all your tracked wallets
/balance - Check balances of all wallets with {current_currency} values
/remove - Remove a wallet from tracking
/currency - Change your preferred currency (USD/CAD)
/help - Show detailed help information

Get started by generating a new wallet with /generate or track an existing one with /add!
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    """
    help_message = """
📖 **Wallet Tracker Bot Help**

**Commands:**

/generate - Generate a new wallet
   • Select blockchain (BTC, ETH, BSC, or SOL)
   • Receive mnemonic, address, and private key
   • Optionally add to tracking automatically

/add - Add an existing wallet
   • You'll be prompted to enter the wallet address
   • Select the blockchain (BTC, ETH, BSC, or SOL)
   • Optionally add a label

/list - View all tracked wallets
   • Shows wallet addresses, blockchains, and labels

/balance - Check current balances
   • Fetches real-time balance for all wallets
   • Shows total value per blockchain

/remove - Remove a wallet
   • Select from your tracked wallets to remove

/currency - Change your preferred currency
   • Switch between USD and CAD for balance displays

/help - Show this help message

**Supported Blockchains:**
• Bitcoin (BTC) - via BlockCypher (no API key needed)
• Ethereum (ETH) - via Etherscan
• Binance Smart Chain (BSC) - via Ankr RPC (no API key needed)
• Solana (SOL) - via Solscan

**Tips:**
• Use labels to easily identify your wallets
• Balances are fetched in real-time
• You can track multiple wallets per blockchain

Need more help? Contact the bot administrator.
"""
    await update.message.reply_text(help_message)


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /currency command - allow user to change preferred currency.
    """
    user_id = update.effective_user.id
    current_currency = tracker.get_user_currency(user_id)

    keyboard = [
        [
            InlineKeyboardButton("💵 USD", callback_data='currency_USD'),
            InlineKeyboardButton("🍁 CAD", callback_data='currency_CAD')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"**Current Currency:** {current_currency}\n\n"
        "Select your preferred currency for balance displays:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle currency selection callback.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    currency = query.data.replace('currency_', '')

    success = tracker.set_user_currency(user_id, currency)

    if success:
        await query.edit_message_text(
            f"✅ Currency preference updated to **{currency}**!\n\n"
            f"All balance displays will now show values in {currency}.\n"
            f"Use /balance to see your updated wallet values.",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Failed to update currency preference.")


async def add_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the wallet addition conversation.
    """
    await update.message.reply_text(
        "Let's add a new wallet! 📝\n\n"
        "Please enter the wallet address you want to track:"
    )
    return WAITING_FOR_ADDRESS


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive wallet address and ask for blockchain.
    """
    address = update.message.text.strip()
    context.user_data['address'] = address

    keyboard = [
        [
            InlineKeyboardButton("Bitcoin (BTC)", callback_data='blockchain_BTC')
        ],
        [
            InlineKeyboardButton("Ethereum (ETH)", callback_data='blockchain_ETH'),
            InlineKeyboardButton("Binance Smart Chain (BSC)", callback_data='blockchain_BSC')
        ],
        [
            InlineKeyboardButton("Solana (SOL)", callback_data='blockchain_SOL')
        ],
        [
            InlineKeyboardButton("Cancel", callback_data='cancel')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Address received: `{address}`\n\n"
        "Now, select the blockchain for this wallet:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAITING_FOR_BLOCKCHAIN


async def receive_blockchain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive blockchain selection and ask for label.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await query.edit_message_text("Wallet addition cancelled.")
        return ConversationHandler.END

    blockchain = query.data.replace('blockchain_', '')
    context.user_data['blockchain'] = blockchain

    await query.edit_message_text(
        f"Blockchain: {blockchain}\n\n"
        "Finally, enter a label for this wallet (or type 'skip' to use default):"
    )
    return WAITING_FOR_LABEL


async def receive_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive label and complete wallet addition.
    """
    label = update.message.text.strip()
    if label.lower() == 'skip':
        label = None

    address = context.user_data.get('address')
    blockchain = context.user_data.get('blockchain')
    user_id = update.effective_user.id

    try:
        result = tracker.add_wallet(user_id, address, blockchain, label)

        if result['success']:
            await update.message.reply_text(
                f"✅ {result['message']}\n\n"
                "Use /balance to check the wallet balance!"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")

    except ValueError as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error adding wallet: {e}")
        await update.message.reply_text("❌ An error occurred while adding the wallet.")

    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the conversation.
    """
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /list command - show all tracked wallets.
    """
    user_id = update.effective_user.id
    wallets = tracker.get_user_wallets(user_id)

    if not wallets:
        await update.message.reply_text(
            "You don't have any tracked wallets yet.\n"
            "Use /add to add your first wallet!"
        )
        return

    message = "📋 **Your Tracked Wallets:**\n\n"

    for i, wallet in enumerate(wallets, 1):
        message += f"{i}. **{wallet['label']}**\n"
        message += f"   • Address: `{wallet['address']}`\n"
        message += f"   • Blockchain: {wallet['blockchain']}\n"
        message += f"   • Added: {wallet['added_at'][:10]}\n\n"

    message += f"Total wallets: {len(wallets)}"

    await update.message.reply_text(message, parse_mode='Markdown')


async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /balance command - check balances for all wallets.
    """
    user_id = update.effective_user.id
    wallets = tracker.get_user_wallets(user_id)

    if not wallets:
        await update.message.reply_text(
            "You don't have any tracked wallets yet.\n"
            "Use /add to add your first wallet!"
        )
        return

    user_currency = tracker.get_user_currency(user_id)
    await update.message.reply_text(f"🔄 Fetching balances and {user_currency} prices... This may take a moment.")

    balances = tracker.get_all_balances(user_id)
    totals = tracker.get_total_value(user_id)

    message = f"💰 **Wallet Balances** ({user_currency}):\n\n"

    for balance in balances:
        status_icon = "✅" if balance['status'] == 'success' else "❌"
        message += f"{status_icon} **{balance['label']}**\n"
        message += f"   • Address: `{balance['address']}`\n"
        message += f"   • Blockchain: {balance['blockchain']}\n"

        if balance['status'] == 'success' and balance['balance'] is not None:
            # Format with fiat value
            formatted_balance = format_fiat_value(
                balance['balance'],
                balance['blockchain'],
                user_currency
            )
            message += f"   • Balance: **{formatted_balance}**\n"
        else:
            message += "   • Balance: Error fetching balance\n"

        message += "\n"

    message += "**Total Balances:**\n"
    for blockchain, total in totals.items():
        if total > 0:
            formatted_total = format_fiat_value(total, blockchain, user_currency)
            message += f"• {formatted_total}\n"

    # Calculate and show total portfolio value in fiat
    total_fiat = get_total_value_in_fiat(totals, user_currency)
    if total_fiat is not None:
        currency_symbol = '$' if user_currency == 'USD' else 'CAD $'
        message += f"\n**Total Portfolio Value:** {currency_symbol}{total_fiat:,.2f} {user_currency}\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def remove_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /remove command - show wallets to remove.
    """
    user_id = update.effective_user.id
    wallets = tracker.get_user_wallets(user_id)

    if not wallets:
        await update.message.reply_text(
            "You don't have any tracked wallets to remove."
        )
        return

    keyboard = []
    for i, wallet in enumerate(wallets):
        button_text = f"{wallet['label']} ({wallet['blockchain']})"
        callback_data = f"remove_{i}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton("Cancel", callback_data='cancel_remove')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select a wallet to remove:",
        reply_markup=reply_markup
    )


async def handle_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle wallet removal callback.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_remove':
        await query.edit_message_text("Removal cancelled.")
        return

    user_id = update.effective_user.id
    wallet_index = int(query.data.replace('remove_', ''))
    wallets = tracker.get_user_wallets(user_id)

    if wallet_index >= len(wallets):
        await query.edit_message_text("❌ Invalid wallet selection.")
        return

    wallet = wallets[wallet_index]
    result = tracker.remove_wallet(user_id, wallet['address'], wallet['blockchain'])

    if result['success']:
        await query.edit_message_text(f"✅ {result['message']}")
    else:
        await query.edit_message_text(f"❌ {result['message']}")


async def generate_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the wallet generation conversation.
    """
    keyboard = [
        [
            InlineKeyboardButton("Bitcoin (BTC)", callback_data='generate_BTC')
        ],
        [
            InlineKeyboardButton("Ethereum (ETH)", callback_data='generate_ETH'),
            InlineKeyboardButton("Binance Smart Chain (BSC)", callback_data='generate_BSC')
        ],
        [
            InlineKeyboardButton("Solana (SOL)", callback_data='generate_SOL')
        ],
        [
            InlineKeyboardButton("All Chains (Multi-Chain)", callback_data='generate_ALL')
        ],
        [
            InlineKeyboardButton("Cancel", callback_data='cancel_generate')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔐 **Wallet Generator**\n\n"
        "Select which blockchain wallet(s) you want to generate:\n\n"
        "⚠️ **IMPORTANT SECURITY WARNING:**\n"
        "• Your mnemonic and private keys will be shown ONCE\n"
        "• Write them down and store safely offline\n"
        "• Never share your mnemonic or private keys\n"
        "• Loss of mnemonic = loss of funds",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAITING_FOR_GENERATE_BLOCKCHAIN


async def receive_generate_blockchain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Receive blockchain selection and show preparation warning.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_generate':
        await query.edit_message_text("Wallet generation cancelled.")
        return ConversationHandler.END

    selected_chain = query.data.replace('generate_', '')
    context.user_data['selected_chain'] = selected_chain

    # Show preparation warning BEFORE generating
    keyboard = [
        [InlineKeyboardButton("✅ I'm Ready - Show My Wallet", callback_data='ready_to_see')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_generate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    chain_name = "Multi-Chain" if selected_chain == 'ALL' else selected_chain

    await query.edit_message_text(
        f"🔐 **Generating {chain_name} Wallet**\n\n"
        "⚠️ **CRITICAL: READ BEFORE PROCEEDING** ⚠️\n\n"
        "📝 **What You Need:**\n"
        "1. **Pen and paper** (NOT digital notes!)\n"
        "2. A **safe place** to store the paper\n"
        "3. **5 minutes** of uninterrupted time\n\n"
        "⚠️ **Important Rules:**\n"
        "• Your mnemonic will be shown **ONLY ONCE**\n"
        "• You **MUST write it down** on paper\n"
        "• **DO NOT screenshot** or save digitally\n"
        "• **DO NOT share** with anyone, ever\n"
        "• If you lose it, **your funds are gone forever**\n\n"
        "🔒 **This message will disappear** after you confirm!\n\n"
        "Are you ready with pen and paper?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAITING_FOR_READY_CONFIRMATION


async def confirm_ready_to_see_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    User confirmed they're ready - now generate and show the wallet.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_generate':
        await query.edit_message_text("Wallet generation cancelled. Your security is important!")
        context.user_data.clear()
        return ConversationHandler.END

    selected_chain = context.user_data.get('selected_chain')
    if not selected_chain:
        await query.edit_message_text("❌ Error: Session expired. Please use /generate again.")
        return ConversationHandler.END

    # Show generating message
    await query.edit_message_text("🔄 Generating your secure wallet... Please wait.")

    try:
        # Generate multi-chain wallet
        wallet = generate_multi_chain_wallet(word_count=12, derivation_index=0)

        # Prepare message based on selection
        if selected_chain == 'ALL':
            # Show all chains
            message = "✅ **Multi-Chain Wallet Generated Successfully!**\n\n"
            message += f"🔑 **Mnemonic (12 words):**\n`{wallet['mnemonic']}`\n\n"
            message += "⚠️ **WRITE THIS DOWN AND STORE SAFELY!**\n\n"
            message += "📍 **Your Addresses:**\n\n"

            for chain, data in wallet['wallets'].items():
                message += f"**{chain.upper()}:**\n"
                message += f"Address: `{data['address']}`\n"
                message += f"Path: `{data['derivationPath']}`\n\n"

            message += "🔐 **Private Keys:**\n"
            message += "⚠️ **EXTREMELY SENSITIVE - NEVER SHARE!**\n"
            message += "⚠️ **You need these to import into wallet apps**\n\n"

            for chain, data in wallet['wallets'].items():
                pk = data['privateKey']
                # Show FULL private key - user needs it to import wallet
                message += f"**{chain.upper()}:**\n`{pk}`\n\n"

            # Store full wallet info for potential adding to tracker
            context.user_data['generated_wallet'] = {
                'mnemonic': wallet['mnemonic'],
                'wallets': wallet['wallets'],
                'selected_chain': 'ALL'
            }

        else:
            # Show single chain
            chain_lower = selected_chain.lower()
            chain_data = wallet['wallets'][chain_lower]

            message = f"✅ **{selected_chain} Wallet Generated Successfully!**\n\n"
            message += f"🔑 **Mnemonic (12 words):**\n`{wallet['mnemonic']}`\n\n"
            message += "⚠️ **WRITE THIS DOWN AND STORE SAFELY!**\n\n"
            message += f"📍 **{selected_chain} Address:**\n`{chain_data['address']}`\n\n"
            message += f"🔐 **Private Key:**\n"
            message += "⚠️ **NEVER SHARE THIS!**\n"
            message += "⚠️ **You need this to import into wallet apps**\n\n"

            pk = chain_data['privateKey']
            # Show FULL private key - user needs it to import wallet
            message += f"`{pk}`\n\n"
            message += f"📂 Derivation Path: `{chain_data['derivationPath']}`\n\n"

            # Store wallet info for potential adding to tracker
            context.user_data['generated_wallet'] = {
                'mnemonic': wallet['mnemonic'],
                'address': chain_data['address'],
                'blockchain': selected_chain,
                'private_key': chain_data['privateKey'],
                'selected_chain': selected_chain
            }

        message += "\n" + "="*40 + "\n"
        message += "⚠️ **WRITE THIS DOWN NOW!** ⚠️\n"
        message += "📝 Copy the mnemonic to paper carefully\n"
        message += "✅ Double-check every word\n"
        message += "🔒 Store in a secure location\n\n"

        # Send the wallet information
        await query.edit_message_text(message, parse_mode='Markdown')

        # Ask for written confirmation
        keyboard = [
            [InlineKeyboardButton("✅ I Have Written It Down", callback_data='written_confirmed')],
            [InlineKeyboardButton("📝 I Need More Time", callback_data='need_more_time')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "⚠️ **IMPORTANT CONFIRMATION** ⚠️\n\n"
            "Have you written down your mnemonic on paper?\n\n"
            "**Before clicking 'I Have Written It Down':**\n"
            "✓ Check you wrote all 12 words correctly\n"
            "✓ Check the spelling of each word\n"
            "✓ Check you wrote them in the correct order\n"
            "✓ Store the paper in a safe place\n\n"
            "🔒 Once you confirm, we'll ask if you want to track this wallet.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return WAITING_FOR_WRITTEN_CONFIRMATION

    except Exception as e:
        logger.error(f"Error generating wallet: {e}")
        await query.edit_message_text(
            f"❌ Error generating wallet: {str(e)}\n\n"
            "Please try again with /generate"
        )
        return ConversationHandler.END


async def confirm_written_down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle confirmation that user has written down the mnemonic.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'need_more_time':
        await query.edit_message_text(
            "✅ Take your time!\n\n"
            "Make sure you've written down:\n"
            "• All 12 words of your mnemonic\n"
            "• In the correct order\n"
            "• With correct spelling\n\n"
            "Scroll up to see your wallet information again.\n"
            "When you're ready, use /generate to create a new wallet\n"
            "or /add to track an existing wallet."
        )
        context.user_data.clear()
        return ConversationHandler.END

    # User confirmed they wrote it down
    generated_wallet = context.user_data.get('generated_wallet')
    if not generated_wallet:
        await query.edit_message_text("❌ Session expired. Please use /generate again.")
        return ConversationHandler.END

    selected_chain = generated_wallet.get('selected_chain')

    # Ask if they want to add to tracking
    if selected_chain != 'ALL':
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Add to Tracking", callback_data='add_generated_yes')],
            [InlineKeyboardButton("❌ No Thanks", callback_data='add_generated_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "✅ **Great! Your mnemonic is safely written down.**\n\n"
            f"Would you like to add your {selected_chain} wallet to tracking?\n\n"
            "This will let you check the balance easily with /balance command.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return WAITING_FOR_ADD_GENERATED
    else:
        # For multi-chain, ask which one(s) to add
        keyboard = []
        for chain in ['BTC', 'ETH', 'BSC', 'SOL']:
            keyboard.append([InlineKeyboardButton(f"Add {chain} to Tracking", callback_data=f'add_multi_{chain}')])
        keyboard.append([InlineKeyboardButton("✅ Done - Don't Add Any", callback_data='add_generated_no')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "✅ **Great! Your mnemonic is safely written down.**\n\n"
            "Select which wallet(s) you want to add to tracking:\n"
            "(You can track them all or just some)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return WAITING_FOR_ADD_GENERATED


async def receive_add_generated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle adding generated wallet to tracking.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'add_generated_no':
        await query.edit_message_text(
            "✅ Wallet generated! Remember to save your mnemonic safely.\n\n"
            "You can always add the wallet to tracking later using /add"
        )
        context.user_data.clear()
        return ConversationHandler.END

    user_id = update.effective_user.id
    generated_wallet = context.user_data.get('generated_wallet')

    if not generated_wallet:
        await query.edit_message_text("❌ Wallet information not found. Please generate a new wallet.")
        return ConversationHandler.END

    try:
        # Handle multi-chain adds
        if query.data.startswith('add_multi_'):
            chain = query.data.replace('add_multi_', '')
            chain_lower = chain.lower()

            # Get the wallet data from context
            wallet_data = generated_wallet['wallets'][chain_lower]
            address = wallet_data['address']

            # Add to tracker
            label = f"Generated {chain} Wallet"
            result = tracker.add_wallet(user_id, address, chain, label)

            if result['success']:
                await query.message.reply_text(f"✅ {chain} wallet added to tracking!")
            else:
                await query.message.reply_text(f"❌ Failed to add {chain} wallet: {result['message']}")

            # Don't end conversation, allow adding more
            return WAITING_FOR_ADD_GENERATED

        # Handle single chain add
        elif query.data == 'add_generated_yes':
            address = generated_wallet['address']
            blockchain = generated_wallet['blockchain']
            label = f"Generated {blockchain} Wallet"

            result = tracker.add_wallet(user_id, address, blockchain, label)

            if result['success']:
                await query.edit_message_text(
                    f"✅ {result['message']}\n\n"
                    "Use /balance to check your wallet balance!"
                )
            else:
                await query.edit_message_text(f"❌ {result['message']}")

            context.user_data.clear()
            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error adding generated wallet: {e}")
        await query.edit_message_text(f"❌ Error adding wallet: {str(e)}")
        context.user_data.clear()
        return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.
    """
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """
    Main function to start the bot.
    """
    # Create the Application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler for adding wallets
    add_wallet_conv = ConversationHandler(
        entry_points=[CommandHandler('add', add_wallet_start)],
        states={
            WAITING_FOR_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)],
            WAITING_FOR_BLOCKCHAIN: [CallbackQueryHandler(receive_blockchain)],
            WAITING_FOR_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_label)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add conversation handler for generating wallets
    generate_wallet_conv = ConversationHandler(
        entry_points=[CommandHandler('generate', generate_wallet_start)],
        states={
            WAITING_FOR_GENERATE_BLOCKCHAIN: [CallbackQueryHandler(receive_generate_blockchain, pattern='^generate_|^cancel_generate')],
            WAITING_FOR_READY_CONFIRMATION: [CallbackQueryHandler(confirm_ready_to_see_wallet, pattern='^ready_to_see|^cancel_generate')],
            WAITING_FOR_WRITTEN_CONFIRMATION: [CallbackQueryHandler(confirm_written_down, pattern='^written_confirmed|^need_more_time')],
            WAITING_FOR_ADD_GENERATED: [CallbackQueryHandler(receive_add_generated, pattern='^add_generated_|^add_multi_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('currency', currency_command))
    application.add_handler(generate_wallet_conv)
    application.add_handler(add_wallet_conv)
    application.add_handler(CommandHandler('list', list_wallets))
    application.add_handler(CommandHandler('balance', check_balance))
    application.add_handler(CommandHandler('remove', remove_wallet_command))
    application.add_handler(CallbackQueryHandler(handle_remove_callback, pattern='^remove_'))
    application.add_handler(CallbackQueryHandler(handle_currency_callback, pattern='^currency_'))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Wallet Tracker Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
