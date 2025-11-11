"""
Example: Practical usage of the multi-chain wallet generator.

SECURITY WARNING:
This example is for educational purposes only. In production:
- NEVER print private keys or mnemonics
- Store mnemonics securely (hardware wallet, encrypted storage)
- Use environment variables for sensitive data
- Implement proper access controls
"""

from wallet_generator import (
    generate_multi_chain_wallet,
    restore_from_mnemonic,
    validate_mnemonic
)
import json


def example_1_generate_new_wallet():
    """
    Example 1: Generate a new multi-chain wallet for a user.

    Use case: User wants to create new wallets across all chains.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Generate New Wallet")
    print("="*80 + "\n")

    # Generate 12-word mnemonic wallet
    wallet = generate_multi_chain_wallet(word_count=12)

    print("✓ New wallet created!")
    print(f"\n{wallet['warning']}\n")
    print("WRITE THIS DOWN AND STORE IT SAFELY:")
    print(f"Mnemonic: {wallet['mnemonic']}")
    print("\nYour addresses:")

    for chain, data in wallet['wallets'].items():
        print(f"  {chain.upper()}: {data['address']}")

    print("\nYou can now send crypto to these addresses.")
    print("Keep your mnemonic safe - it's the only way to recover your funds!")

    return wallet


def example_2_restore_existing_wallet():
    """
    Example 2: Restore wallet from existing mnemonic.

    Use case: User has a mnemonic and wants to get their addresses.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Restore Existing Wallet")
    print("="*80 + "\n")

    # Example mnemonic (DO NOT USE THIS IN PRODUCTION - it's public!)
    example_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    print(f"Restoring wallet from mnemonic:\n{example_mnemonic}\n")

    # First validate it
    if not validate_mnemonic(example_mnemonic):
        print("✗ Invalid mnemonic!")
        return None

    print("✓ Mnemonic is valid")

    # Restore wallet
    wallet = restore_from_mnemonic(example_mnemonic)

    print("\n✓ Wallet restored!")
    print("\nYour addresses:")

    for chain, data in wallet['wallets'].items():
        print(f"  {chain.upper()}: {data['address']}")

    return wallet


def example_3_generate_multiple_accounts():
    """
    Example 3: Generate multiple accounts from same mnemonic.

    Use case: User wants multiple wallets (e.g., savings, trading, business).
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Multiple Accounts from One Mnemonic")
    print("="*80 + "\n")

    # Use known mnemonic for demonstration
    mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    print("Creating 3 accounts from the same mnemonic...\n")

    accounts = {
        'Savings': restore_from_mnemonic(mnemonic, derivation_index=0),
        'Trading': restore_from_mnemonic(mnemonic, derivation_index=1),
        'Business': restore_from_mnemonic(mnemonic, derivation_index=2)
    }

    for account_name, wallet in accounts.items():
        print(f"{account_name} Account (Index {wallet['derivationIndex']}):")
        print(f"  ETH: {wallet['wallets']['eth']['address']}")
        print(f"  BTC: {wallet['wallets']['btc']['address']}")
        print()

    print("All accounts can be restored with the same mnemonic!")
    print("Just remember which derivation index is for which purpose.")


def example_4_export_addresses_only():
    """
    Example 4: Export only addresses (safe to share).

    Use case: You want to share addresses without exposing private keys.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Export Addresses Only (Safe to Share)")
    print("="*80 + "\n")

    wallet = generate_multi_chain_wallet()

    # Extract only public addresses (safe to share)
    public_data = {
        'addresses': {
            chain: data['address']
            for chain, data in wallet['wallets'].items()
        },
        'createdAt': wallet['createdAt'],
        'note': 'These are public addresses - safe to share for receiving funds'
    }

    print("Safe to share (addresses only):")
    print(json.dumps(public_data, indent=2))

    print("\n⚠️ NEVER share your mnemonic or private keys!")
    print(f"Mnemonic (KEEP SECRET): {wallet['mnemonic']}")


def example_5_validate_mnemonic():
    """
    Example 5: Validate user-provided mnemonic before using it.

    Use case: User inputs their mnemonic and you want to verify it's valid.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Validate Mnemonic")
    print("="*80 + "\n")

    test_mnemonics = [
        {
            'mnemonic': 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about',
            'description': 'Valid 12-word mnemonic'
        },
        {
            'mnemonic': 'invalid word here',
            'description': 'Invalid mnemonic (wrong words)'
        },
        {
            'mnemonic': 'abandon abandon abandon',
            'description': 'Invalid mnemonic (wrong length)'
        }
    ]

    for test in test_mnemonics:
        is_valid = validate_mnemonic(test['mnemonic'])
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"{status}: {test['description']}")
        print(f"  Mnemonic: {test['mnemonic'][:50]}...")
        print()


def example_6_integration_with_tracker():
    """
    Example 6: Generate wallet and add to tracker.

    Use case: Generate new wallet and immediately add it to the tracking bot.
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Integration with Wallet Tracker Bot")
    print("="*80 + "\n")

    print("Step 1: Generate new wallet")
    wallet = generate_multi_chain_wallet()

    print(f"✓ Generated wallet with mnemonic:\n  {wallet['mnemonic']}\n")

    print("Step 2: Extract addresses for tracking")
    addresses = []
    for chain, data in wallet['wallets'].items():
        addresses.append({
            'blockchain': chain.upper(),
            'address': data['address'],
            'label': f'My {chain.upper()} Wallet'
        })

    print("\nAddresses ready to add to tracker:")
    for addr in addresses:
        print(f"  {addr['label']}: {addr['address']}")

    print("\nStep 3: In your Telegram bot, you would now:")
    print("  1. Use /add command")
    print("  2. Enter each address")
    print("  3. Select blockchain")
    print("  4. Add label")

    print("\nStep 4: Check balances with /balance command")
    print("\n⚠️ Store your mnemonic safely! You'll need it to access your funds.")


def main():
    """Run all examples."""
    print("\n" + "*"*80)
    print(" MULTI-CHAIN WALLET GENERATOR - PRACTICAL EXAMPLES")
    print("*"*80)

    # Run examples
    example_1_generate_new_wallet()
    example_2_restore_existing_wallet()
    example_3_generate_multiple_accounts()
    example_4_export_addresses_only()
    example_5_validate_mnemonic()
    example_6_integration_with_tracker()

    # Final warnings
    print("\n" + "="*80)
    print(" SECURITY BEST PRACTICES")
    print("="*80)
    print("""
1. NEVER share your mnemonic or private keys
2. Store mnemonic offline (paper, hardware wallet)
3. Make multiple backups in secure locations
4. Never enter mnemonic on untrusted websites
5. Test with small amounts first
6. Use hardware wallets for large amounts
7. Double-check addresses before sending funds
8. Be aware of phishing attempts
9. Keep your computer secure (antivirus, updates)
10. Consider using multi-signature for large holdings

Remember: "Not your keys, not your crypto"
If you lose your mnemonic, your funds are GONE FOREVER.
""")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
