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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    """
    user = update.effective_user
    welcome_message = f"""
👋 Welcome to Wallet Tracker Bot, {user.first_name}!

I help you track cryptocurrency wallet balances across multiple blockchains.

**Supported Blockchains:**
• Ethereum (ETH)
• Binance Smart Chain (BSC)
• Solana (SOL)

**Available Commands:**
/start - Show this welcome message
/add - Add a new wallet to track
/list - List all your tracked wallets
/balance - Check balances of all wallets
/remove - Remove a wallet from tracking
/help - Show detailed help information

Get started by adding your first wallet with /add!
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    """
    help_message = """
📖 **Wallet Tracker Bot Help**

**Commands:**

/add - Add a new wallet
   • You'll be prompted to enter the wallet address
   • Select the blockchain (ETH, BSC, or SOL)
   • Optionally add a label

/list - View all tracked wallets
   • Shows wallet addresses, blockchains, and labels

/balance - Check current balances
   • Fetches real-time balance for all wallets
   • Shows total value per blockchain

/remove - Remove a wallet
   • Select from your tracked wallets to remove

/help - Show this help message

**Supported Blockchains:**
• Ethereum (ETH) - via Etherscan
• Binance Smart Chain (BSC) - via BSCScan
• Solana (SOL) - via Solscan

**Tips:**
• Use labels to easily identify your wallets
• Balances are fetched in real-time
• You can track multiple wallets per blockchain

Need more help? Contact the bot administrator.
"""
    await update.message.reply_text(help_message)


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

    await update.message.reply_text("🔄 Fetching balances... This may take a moment.")

    balances = tracker.get_all_balances(user_id)
    totals = tracker.get_total_value(user_id)

    message = "💰 **Wallet Balances:**\n\n"

    for balance in balances:
        status_icon = "✅" if balance['status'] == 'success' else "❌"
        message += f"{status_icon} **{balance['label']}**\n"
        message += f"   • Address: `{balance['address']}`\n"
        message += f"   • Blockchain: {balance['blockchain']}\n"

        if balance['status'] == 'success' and balance['balance'] is not None:
            message += f"   • Balance: **{balance['balance']:.6f}** {balance['blockchain']}\n"
        else:
            message += "   • Balance: Error fetching balance\n"

        message += "\n"

    message += "**Total Balances:**\n"
    for blockchain, total in totals.items():
        if total > 0:
            message += f"• {blockchain}: **{total:.6f}**\n"

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

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(add_wallet_conv)
    application.add_handler(CommandHandler('list', list_wallets))
    application.add_handler(CommandHandler('balance', check_balance))
    application.add_handler(CommandHandler('remove', remove_wallet_command))
    application.add_handler(CallbackQueryHandler(handle_remove_callback, pattern='^remove_'))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Wallet Tracker Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
