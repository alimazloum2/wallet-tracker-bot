"""
Test script for multi-chain wallet generator.

Run this after installing dependencies:
    pip install -r requirements.txt

This script demonstrates:
1. Generating a new multi-chain wallet
2. Restoring a wallet from mnemonic
3. Generating multiple wallets from same mnemonic (different derivation indices)
4. Validating mnemonics
"""

from wallet_generator import (
    generate_multi_chain_wallet,
    restore_from_mnemonic,
    validate_mnemonic,
    WalletGeneratorError
)


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "=" * 80)
    if title:
        print(f" {title}")
        print("=" * 80)
    print()


def print_wallet_info(wallet_data, show_private_keys=False):
    """
    Print wallet information in a formatted way.

    Args:
        wallet_data: Wallet dictionary from generate_multi_chain_wallet()
        show_private_keys: If True, show full private keys (DANGEROUS!)
    """
    print(f"Created: {wallet_data['createdAt']}")
    print(f"Derivation Index: {wallet_data.get('derivationIndex', 0)}")
    print(f"Restored: {wallet_data.get('restored', False)}")
    print()
    print("⚠️  WARNING:", wallet_data['warning'])
    print()
    print("Mnemonic (12 words):")
    print(f"  {wallet_data['mnemonic']}")
    print()
    print("Wallets Generated:")

    for chain, data in wallet_data['wallets'].items():
        print(f"\n{chain.upper()} Wallet:")
        print(f"  Derivation Path: {data['derivationPath']}")
        print(f"  Address: {data['address']}")

        if show_private_keys:
            print(f"  Private Key: {data['privateKey']}")
        else:
            # Show truncated private key for safety
            pk = data['privateKey']
            print(f"  Private Key: {pk[:10]}...{pk[-10:]} (truncated for safety)")


def test_generate_new_wallet():
    """Test 1: Generate a new multi-chain wallet."""
    print_separator("TEST 1: Generate New Multi-Chain Wallet")

    try:
        # Generate with 12-word mnemonic
        wallet = generate_multi_chain_wallet(word_count=12, derivation_index=0)

        print("✓ Successfully generated new wallet!")
        print_wallet_info(wallet, show_private_keys=False)

        return wallet

    except WalletGeneratorError as e:
        print(f"✗ Failed to generate wallet: {e}")
        return None


def test_restore_from_mnemonic(mnemonic):
    """Test 2: Restore wallet from existing mnemonic."""
    print_separator("TEST 2: Restore Wallet from Mnemonic")

    try:
        # Restore wallet
        restored = restore_from_mnemonic(mnemonic, derivation_index=0)

        print("✓ Successfully restored wallet from mnemonic!")
        print_wallet_info(restored, show_private_keys=False)

        return restored

    except WalletGeneratorError as e:
        print(f"✗ Failed to restore wallet: {e}")
        return None


def test_verify_restoration(original, restored):
    """Test 3: Verify that restored wallet matches original."""
    print_separator("TEST 3: Verify Restoration Accuracy")

    if not original or not restored:
        print("✗ Cannot verify - original or restored wallet is missing")
        return False

    print("Checking if restored addresses match original addresses...")
    print()

    all_match = True
    for chain in ['eth', 'bsc', 'sol', 'btc']:
        original_addr = original['wallets'][chain]['address']
        restored_addr = restored['wallets'][chain]['address']
        match = original_addr == restored_addr

        status = "✓" if match else "✗"
        print(f"{status} {chain.upper():4s}: {restored_addr} {'MATCH' if match else 'MISMATCH'}")

        if not match:
            all_match = False
            print(f"       Original: {original_addr}")

    print()
    if all_match:
        print("✓ All addresses match! Restoration successful.")
    else:
        print("✗ Some addresses don't match! Check derivation logic.")

    return all_match


def test_multiple_wallets_same_mnemonic(mnemonic):
    """Test 4: Generate multiple wallets from same mnemonic using different indices."""
    print_separator("TEST 4: Multiple Wallets from Same Mnemonic")

    print("Generating 3 wallets from the same mnemonic using different derivation indices...")
    print()

    try:
        wallets = []
        for i in range(3):
            wallet = restore_from_mnemonic(mnemonic, derivation_index=i)
            wallets.append(wallet)
            print(f"Wallet #{i}:")
            print(f"  ETH: {wallet['wallets']['eth']['address']}")
            print(f"  BTC: {wallet['wallets']['btc']['address']}")
            print()

        # Verify all addresses are different
        eth_addresses = [w['wallets']['eth']['address'] for w in wallets]
        unique_eth = len(set(eth_addresses)) == len(eth_addresses)

        if unique_eth:
            print("✓ All wallets have unique addresses (as expected)")
        else:
            print("✗ Some addresses are duplicated (unexpected!)")

        return wallets

    except WalletGeneratorError as e:
        print(f"✗ Failed: {e}")
        return []


def test_mnemonic_validation():
    """Test 5: Validate mnemonics."""
    print_separator("TEST 5: Mnemonic Validation")

    test_cases = [
        ("Valid 12-word", "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", True),
        ("Invalid word", "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon invalidword", False),
        ("Wrong word count", "abandon abandon abandon", False),
        ("Empty", "", False),
    ]

    print("Testing mnemonic validation...")
    print()

    for name, mnemonic, expected in test_cases:
        result = validate_mnemonic(mnemonic)
        status = "✓" if result == expected else "✗"
        print(f"{status} {name:20s}: {result} (expected {expected})")


def main():
    """Run all tests."""
    print()
    print("*" * 80)
    print(" MULTI-CHAIN WALLET GENERATOR - TEST SUITE")
    print("*" * 80)

    # Test 1: Generate new wallet
    wallet = test_generate_new_wallet()

    if wallet:
        # Test 2: Restore from mnemonic
        restored = test_restore_from_mnemonic(wallet['mnemonic'])

        # Test 3: Verify restoration
        test_verify_restoration(wallet, restored)

        # Test 4: Multiple wallets from same mnemonic
        test_multiple_wallets_same_mnemonic(wallet['mnemonic'])

    # Test 5: Mnemonic validation
    test_mnemonic_validation()

    print_separator("TESTS COMPLETE")

    print("⚠️  SECURITY REMINDERS:")
    print("  1. Never commit private keys or mnemonics to version control")
    print("  2. Store mnemonics securely (hardware wallet, encrypted backup)")
    print("  3. Never share private keys with anyone")
    print("  4. Test with small amounts first")
    print("  5. Back up your mnemonic in multiple secure locations")
    print()


if __name__ == "__main__":
    main()
