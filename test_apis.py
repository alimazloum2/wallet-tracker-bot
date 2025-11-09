#!/usr/bin/env python3
"""
Test script for blockchain API calls.
Run this to test if your API keys are working correctly.

NOTE: Tests run with 3-second delays between API calls to avoid rate limiting.
"""

import sys
import time
from apis import get_balance, validate_address, BlockchainAPIError
from config import Config

def test_address_validation():
    """Test address validation for different blockchains."""
    print("\n" + "="*60)
    print("TESTING ADDRESS VALIDATION")
    print("="*60)

    # Test ETH addresses
    eth_test_cases = [
        ("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", True),  # Valid
        ("0xcB2F0F0509c534d280249c89B32aE3BFeD983Cbdd2", False),  # Too long (44 chars)
        ("0xInvalidAddress", False),  # Invalid hex
        ("742d35Cc6634C0532925a3b844Bc9e7595f0bEb", False),  # Missing 0x
    ]

    print("\nETH Address Validation:")
    for addr, expected in eth_test_cases:
        result = validate_address(addr, 'ETH')
        status = "✓" if result == expected else "✗"
        print(f"{status} {addr} - Length: {len(addr)} - Valid: {result}")

    # Test SOL addresses
    sol_test_cases = [
        ("5Ey4FfQYuHV5ir9o4vVAGM4tmMsBE1omc6uHw8VuccF4", True),  # Valid
        ("invalid-solana-address-!@#", False),  # Invalid characters
    ]

    print("\nSOL Address Validation:")
    for addr, expected in sol_test_cases:
        result = validate_address(addr, 'SOL')
        status = "✓" if result == expected else "✗"
        print(f"{status} {addr} - Length: {len(addr)} - Valid: {result}")


def test_api_keys():
    """Test if API keys are loaded correctly."""
    print("\n" + "="*60)
    print("TESTING API KEY CONFIGURATION")
    print("="*60)

    api_keys = {
        'TELEGRAM_BOT_TOKEN': Config.TELEGRAM_BOT_TOKEN,
        'ETHERSCAN_API_KEY': Config.ETHERSCAN_API_KEY,
        'BSCSCAN_API_KEY': Config.BSCSCAN_API_KEY,
        'SOLSCAN_API_KEY': Config.SOLSCAN_API_KEY,
    }

    for name, key in api_keys.items():
        if key and len(key) > 5:
            preview = f"{key[:5]}...{key[-3:]}"
            print(f"✓ {name}: {preview} (Length: {len(key)})")
        elif key:
            print(f"✗ {name}: TOO SHORT ({key})")
        else:
            print(f"✗ {name}: NOT SET")


def test_eth_balance():
    """Test Ethereum balance fetching with retry logic."""
    print("\n" + "="*60)
    print("TESTING ETHEREUM BALANCE FETCH")
    print("="*60)

    # Use a known address with balance (Vitalik's address)
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    print(f"\nTesting with address: {test_address}")
    print("Note: Adding 2-second delay to avoid rate limiting...")
    time.sleep(2)

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")
            result = get_balance(test_address, 'ETH')

            if result:
                print(f"\n✓ SUCCESS!")
                print(f"Address: {result['address']}")
                print(f"Balance: {result['balance']} ETH")
                print(f"Balance (wei): {result['balance_wei']}")
                return True
            else:
                print(f"\n✗ ATTEMPT {attempt} FAILED: get_balance returned None")
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        except BlockchainAPIError as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: Unexpected error: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print(f"\n✗ FAILED: All {max_retries} attempts exhausted for ETH balance")
    return False


def test_sol_balance():
    """Test Solana balance fetching with retry logic."""
    print("\n" + "="*60)
    print("TESTING SOLANA BALANCE FETCH")
    print("="*60)

    test_address = "5Ey4FfQYuHV5ir9o4vVAGM4tmMsBE1omc6uHw8VuccF4"

    print(f"\nTesting with address: {test_address}")
    print("Note: Adding 2-second delay to avoid rate limiting...")
    time.sleep(2)

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")
            result = get_balance(test_address, 'SOL')

            if result:
                print(f"\n✓ SUCCESS!")
                print(f"Address: {result['address']}")
                print(f"Balance: {result['balance']} SOL")
                print(f"Balance (lamports): {result['balance_lamports']}")
                return True
            else:
                print(f"\n✗ ATTEMPT {attempt} FAILED: get_balance returned None")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        except BlockchainAPIError as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: Unexpected error: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print(f"\n✗ FAILED: All {max_retries} attempts exhausted for SOL balance")
    return False


def test_bsc_balance():
    """Test BSC balance fetching with retry logic."""
    print("\n" + "="*60)
    print("TESTING BSC BALANCE FETCH")
    print("="*60)

    # Use Binance hot wallet address
    test_address = "0xF977814e90dA44bFA03b6295A0616a897441aceC"

    print(f"\nTesting with address: {test_address}")
    print("Note: Adding 2-second delay to avoid rate limiting...")
    time.sleep(2)

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"\nAttempt {attempt}/{max_retries}...")
            result = get_balance(test_address, 'BSC')

            if result:
                print(f"\n✓ SUCCESS!")
                print(f"Address: {result['address']}")
                print(f"Balance: {result['balance']} BNB")
                print(f"Balance (wei): {result['balance_wei']}")
                return True
            else:
                print(f"\n✗ ATTEMPT {attempt} FAILED: get_balance returned None")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        except BlockchainAPIError as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"\n✗ ATTEMPT {attempt} FAILED: Unexpected error: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print(f"\n✗ FAILED: All {max_retries} attempts exhausted for BSC balance")
    return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("BLOCKCHAIN API TEST SUITE")
    print("="*60)

    try:
        test_api_keys()
        test_address_validation()

        # Ask user which tests to run
        print("\n" + "="*60)
        print("Select tests to run:")
        print("1. Test Ethereum (ETH)")
        print("2. Test Binance Smart Chain (BSC)")
        print("3. Test Solana (SOL)")
        print("4. Test All")
        print("="*60)

        choice = input("\nEnter choice (1-4) or press Enter for all: ").strip()

        if choice == '1':
            test_eth_balance()
        elif choice == '2':
            test_bsc_balance()
        elif choice == '3':
            test_sol_balance()
        else:
            # Run all tests sequentially with delays to avoid rate limiting
            print("\n⏱️  Running all tests with delays between each blockchain...")
            print("This will take approximately 20-30 seconds to complete.\n")

            eth_success = test_eth_balance()
            print("\n⏱️  Waiting 3 seconds before next test...")
            time.sleep(3)

            bsc_success = test_bsc_balance()
            print("\n⏱️  Waiting 3 seconds before next test...")
            time.sleep(3)

            sol_success = test_sol_balance()

            # Summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            print(f"ETH: {'✓ PASSED' if eth_success else '✗ FAILED'}")
            print(f"BSC: {'✓ PASSED' if bsc_success else '✗ FAILED'}")
            print(f"SOL: {'✓ PASSED' if sol_success else '✗ FAILED'}")
            total = sum([eth_success, bsc_success, sol_success])
            print(f"\nTotal: {total}/3 tests passed")
            print("="*60)

        print("\n" + "="*60)
        print("TESTS COMPLETED")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
