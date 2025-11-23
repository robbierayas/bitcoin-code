"""
Configuration for Bitcoin Code Tests

This module stores test private keys, addresses, and other test data
used throughout the test suite.

WARNING: These are test keys only. Never use for real Bitcoin.
"""


# ============================================================================
# TEST PRIVATE KEYS
# ============================================================================

class TestKeys:
    """Test private keys and their corresponding addresses."""

    # Simple test key used in multiple tests
    KEY1_HEX = "0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D"
    KEY1_WIF = "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ"

    # Key 2 - used for address generation tests
    KEY2_HEX = "18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725"
    KEY2_ADDR = "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"

    # Key 3 - myTransaction.py and myWallet.py tests
    KEY3_HEX = "a2d43efac7e99b7e3cf4c07ebfebb3c349d8f2b5b0e1062d9cef93c170d22d4f"

    # Blockchain.info wallet example
    BLOCKCHAIN_INFO_PRIVATE = "8tnArBrrp4KHVjv8WA6HiX4ev56WDhqGA16XJCHJzhNH"
    BLOCKCHAIN_INFO_KEY = "754580de93eea21579441b58e0c9b09f54f6005fc71135f5cfac027394b22caa"
    BLOCKCHAIN_INFO_ADDR = "1EyBEhrriJeghX4iqATQEWDq38Ae8ubBJe"

    # Multibit wallet example
    MULTIBIT_WIF = "5Jhw8B9J9QLaMmcBRfz7x8KkD9gwbNoyBMfWyANqiDwm3FFwgGC"
    MULTIBIT_ADDR = "1EyBEhrriJeghX4iqATQEWDq38Ae8ubBJe"

    # gobittest.appspot.com example
    GOBI_KEY = "BB08A897EA1E422F989D36DE8D8186D8406BE25E577FD2A66976BF172325CDC9"
    GOBI_ADDR = "1MZ1nxFpvUgaPYYWaLPkLGAtKjRqcCwbGh"

    # bitaddress.org example
    BITADDRESS_WIF = "5J8PhneLEaL9qEPvW5voRgrELeXcmM12B6FbiA9wZAwDMnJMb2L"
    BITADDRESS_ADDR = "1Q2SuNLDXDtda7DPnBTocQWtUg1v4xZMrV"

    # Transaction signing test key (133t address)
    TXN_TEST_WIF = "5Kb6aGpijtrb8X28GzmWtbcGZCG8jHQWFJcWugqo3MwKRvC8zyu"
    TXN_TEST_ADDR = "133txdxQmwECTmXqAr9RWNHnzQ175jGb7e"


# ============================================================================
# TEST TRANSACTIONS
# ============================================================================

class TestTransactions:
    """Test transaction data."""

    # Standard test transaction used in multiple tests
    TXN_SIGNED = (
        "0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000"
        "8a47"
        "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01"
        "41"
        "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55"
        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000"
        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000"
    )

    # Signable version of test transaction
    TXN_SIGNABLE = (
        "0100000001a97830933769fe33c6155286ffae34db44c6b8783a2d8ca52ebee6414d399ec300000000"
        "1976a914167c74f7491fe552ce9e1912810a984355b8ee0788ac"
        "ffffffff02015f0000000000001976a914c8e90996c7c6080ee06284600c684ed904d14c5c88ac204e000000000000"
        "1976a914348514b329fda7bd33c7b2336cf7cd1fc9544c0588ac00000000"
        "01000000"
    )

    # Public key from test transaction
    TXN_PUBKEY = "04392b964e911955ed50e4e368a9476bc3f9dcc134280e15636430eb91145dab739f0d68b82cf33003379d885a0b212ac95e9cddfd2d391807934d25995468bc55"

    # DER signature from test transaction
    TXN_SIG_DER = "304402202c2e1a746c556546f2c959e92f2d0bd2678274823cc55e11628284e4a13016f80220797e716835f9dbcddb752cd0115a970a022ea6f2d8edafff6e087f928e41baac01"

    # Transaction details for makeSignedTransaction test
    # https://blockchain.info/tx/901a53e7a3ca96ed0b733c0233aad15f11b0c9e436294aa30c367bf06c3b7be8
    BLOCKCHAIN_TX_HASH = "c39e394d41e6be2ea58c2d3a78b8c644db34aeff865215c633fe6937933078a9"
    BLOCKCHAIN_TX_SOURCE_INDEX = 0
    BLOCKCHAIN_TX_OUTPUTS = [
        [24321, "1KKKK6N21XKo48zWKuQKXdvSsCf95ibHFa"],
        [20000, "15nhZbXnLMknZACbb3Jrf1wPCD9DWAcqd7"]
    ]


# ============================================================================
# TEST SIGNATURES
# ============================================================================

class TestSignatures:
    """Test DER signature data."""

    # DER signature test case
    DER_SIG = "304502204c01fee2d724fb2e34930c658f585d49be2f6ac87c126506c0179e6977716093022100faad0afd3ae536cfe11f83afaba9a8914fc0e70d4c6d1495333b2fb3df6e8cae"
    HEX_SIG = "4c01fee2d724fb2e34930c658f585d49be2f6ac87c126506c0179e6977716093faad0afd3ae536cfe11f83afaba9a8914fc0e70d4c6d1495333b2fb3df6e8cae"


# ============================================================================
# TEST RAW TRANSACTION DATA
# ============================================================================

class TestRawTransactions:
    """Test raw transaction creation data."""

    # http://bitcoin.stackexchange.com/questions/3374/how-to-redeem-a-basic-tx
    RAW_TX_PREV_HASH = "f2b3eb2deb76566e7324307cd47c35eeb88413f971d88519859b1834307ecfec"
    RAW_TX_SOURCE_INDEX = 1
    RAW_TX_SCRIPT_SIG = "76a914010966776006953d5567439e5e39f86a0d273bee88ac"
    RAW_TX_SATOSHIS = 99900000
    RAW_TX_OUTPUT_SCRIPT = "76a914097072524438d003d23a2f23edb65aae1bb3e46988ac"

    RAW_TX_EXPECTED = (
        "0100000001eccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f2"
        "010000001976a914010966776006953d5567439e5e39f86a0d273bee88acffffffff"
        "01605af405000000001976a914097072524438d003d23a2f23edb65aae1bb3e46988ac"
        "0000000001000000"
    )


# ============================================================================
# TEST HD WALLET DATA (BIP32/BIP39)
# ============================================================================

class TestHDWallet:
    """Test mnemonic and HD wallet data."""

    # Test mnemonic (12 words) - REAL WALLET FOR TESTING
    # This wallet has real transaction history - NOT FOR PRODUCTION
    MNEMONIC_12 = "grit problem ball awesome symbol leopard coral toddler must alien ocean satisfy"

    # Test mnemonic (24 words) - DO NOT USE FOR REAL FUNDS
    MNEMONIC_24 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art"

    # Expected addresses for MNEMONIC_12 (Electrum native wallet)
    # NOTE: This is an Electrum NATIVE seed (not BIP39)
    # Uses m/0/x (receiving) and m/1/x (change) derivation
    # Uses COMPRESSED public keys for address generation

    # m/0/0 (first receiving address) - VERIFIED
    EXPECTED_ADDR_0_0 = "1DqEczkgKeQNDHCoMFubQebMEoNW3Bx7X5"
    # m/0/1 (second receiving address)
    EXPECTED_ADDR_0_1 = "1FsARj423XtyNuiLRUEzYZQDZsrKrqaNoV"
    # m/1/0 (first change address) - VERIFIED
    EXPECTED_ADDR_1_0 = "1EGHUD4NTGWR5n1bL9qroHqbTaMoPZE6a7"

    # Known addresses with transaction history
    KNOWN_ADDR_WITH_TXS = "1DqEczkgKeQNDHCoMFubQebMEoNW3Bx7X5"
    KNOWN_CHANGE_ADDR = "1EGHUD4NTGWR5n1bL9qroHqbTaMoPZE6a7"

    # Default derivation path for Bitcoin (BIP44)
    DEFAULT_PATH = "m/44'/0'/0'/0/0"

    # Account paths
    ACCOUNT_0 = "m/44'/0'/0'"
    ACCOUNT_1 = "m/44'/0'/1'"

    # Chain types
    EXTERNAL_CHAIN = 0  # Receiving addresses
    INTERNAL_CHAIN = 1  # Change addresses

    # Electrum master key verification (from Electrum wallet)
    ELECTRUM_MASTER_XPUB = "xpub661MyMwAqRbcFWMdzBLTpwv2egaPXhWBAmoStC5rUkEFZ8RyajXySawMCrH12h1obtVY8pdKAdS8mperMLe6KUyppduasmNHibUnM37nq9q"
    ELECTRUM_ROOT_FINGERPRINT = "f5934df8"


# ============================================================================
# ROLLBACK CONFIGURATION
# ============================================================================

class RollbackConfig:
    """Configuration for rollback mechanisms and performance tracking."""

    # ========================================================================
    # Runner Configuration
    # ========================================================================

    RUNNER_CONFIG = {
        'verbose': True,              # Print detailed output
        'log_to_file': True,          # Save results to JSON files
        'output_dir': 'output',       # Directory for output files
        'show_timing': True,          # Display execution time
        'pretty_print': True,         # Format output nicely
    }

    # ========================================================================
    # RIPEMD-160 Rollback Configuration
    # ========================================================================

    RIPEMD160_CONFIG = {
        'mechanism_type': 'brute',    # Type of mechanism to use
        'verbose': True,              # Print diagnostic output
        'max_iterations': None,       # Maximum iterations (None = unlimited)
    }

    # Test addresses for rollback
    TEST_ADDRESSES = {
        'key1': "12vieiAHxBe4qCUrwvfb2kRkDuc8kQ8qSw",  # From TestKeys.KEY1_HEX
        'key2': "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM",  # From TestKeys.KEY2_HEX
        'key3': "1BTCorgHwCg6u2YSAWKgS17qUad6kHmtQW",  # From TestKeys.KEY3_HEX
    }

    # ========================================================================
    # ECDSA Rollback Configuration
    # ========================================================================

    ECDSA_CONFIG = {
        'mechanism_type': 'brute',    # Type of mechanism to use
        'verbose': True,              # Print diagnostic output
        'max_iterations': None,       # Maximum iterations (None = unlimited)
    }

    # ========================================================================
    # Performance Tracking Configuration
    # ========================================================================

    PERFORMANCE_CONFIG = {
        'enabled': True,              # Enable performance tracking
        'track_memory': True,         # Track memory usage
        'track_cpu': True,            # Track CPU time
        'save_results': True,         # Save performance results to file
        'results_dir': 'output/performance',  # Directory for performance results
        'compare_methods': True,      # Enable method comparison
        'warmup_runs': 0,            # Number of warmup runs before timing
        'repeat_runs': 1,            # Number of times to repeat each test
        'print_summary': True,        # Print summary after each test
    }
