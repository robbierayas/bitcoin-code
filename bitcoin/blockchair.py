"""
Blockchair API Integration

Provides functions to query blockchain data from blockchair.com API.

Functions:
- find_utxos(address): Find unspent transaction outputs for an address
- get_address_balance(address): Get total balance for an address

API Documentation: https://blockchair.com/api/docs
"""

import urllib.request
import urllib.error
import json
import time


class BlockchairError(Exception):
    """Exception raised for Blockchair API errors."""
    pass


def _make_request(url, max_retries=3, retry_delay=1):
    """
    Make HTTP request with retries.

    Args:
        url (str): URL to request
        max_retries (int): Maximum number of retries
        retry_delay (int): Delay between retries in seconds

    Returns:
        dict: JSON response

    Raises:
        BlockchairError: If request fails
    """
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise BlockchairError(f"Failed to fetch data from Blockchair: {e}")
        except json.JSONDecodeError as e:
            raise BlockchairError(f"Failed to parse Blockchair response: {e}")

    raise BlockchairError(f"Max retries ({max_retries}) exceeded")


def find_utxos(address, min_confirmations=1):
    """
    Find unspent transaction outputs (UTXOs) for a Bitcoin address.

    Args:
        address (str): Bitcoin address
        min_confirmations (int): Minimum confirmations required (default: 1)

    Returns:
        list: List of UTXO dictionaries, each containing:
            - txid (str): Transaction ID
            - vout (int): Output index
            - value (int): Value in satoshis
            - confirmations (int): Number of confirmations
            - script_pubkey (str): Script public key hex

    Example:
        >>> utxos = find_utxos("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        >>> for utxo in utxos:
        ...     print(f"TXID: {utxo['txid']}, Value: {utxo['value']} sats")

    Raises:
        BlockchairError: If API request fails
    """
    # Blockchair API endpoint for address data
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"

    # Make request
    response = _make_request(url)

    # Check for errors
    if 'data' not in response:
        raise BlockchairError(f"Unexpected API response format: {response}")

    address_data = response['data'].get(address)
    if not address_data:
        raise BlockchairError(f"No data found for address: {address}")

    # Get UTXOs
    utxos = address_data.get('utxo', [])

    # Filter by confirmations and format
    result = []
    context = response.get('context', {})
    current_block = context.get('state', 0)

    for utxo in utxos:
        confirmations = current_block - utxo.get('block_id', 0) + 1

        # Skip if below minimum confirmations
        if confirmations < min_confirmations:
            continue

        result.append({
            'txid': utxo.get('transaction_hash'),
            'vout': utxo.get('index'),
            'value': utxo.get('value'),
            'confirmations': confirmations,
            'script_pubkey': utxo.get('script_hex', '')
        })

    return result


def get_address_balance(address):
    """
    Get balance and transaction info for a Bitcoin address.

    Args:
        address (str): Bitcoin address

    Returns:
        dict: Balance information containing:
            - confirmed (int): Confirmed balance in satoshis
            - unconfirmed (int): Unconfirmed balance in satoshis
            - total (int): Total balance in satoshis
            - transaction_count (int): Number of transactions (0 = unused address)

    Example:
        >>> balance = get_address_balance("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        >>> print(f"Balance: {balance['total']} satoshis")
        >>> print(f"Has been used: {balance['transaction_count'] > 0}")

    Raises:
        BlockchairError: If API request fails
    """
    # Blockchair API endpoint
    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"

    # Make request
    response = _make_request(url)

    # Check for errors
    if 'data' not in response:
        raise BlockchairError(f"Unexpected API response format: {response}")

    address_data = response['data'].get(address)
    if not address_data:
        raise BlockchairError(f"No data found for address: {address}")

    # Get address info
    address_info = address_data.get('address', {})

    return {
        'confirmed': address_info.get('balance', 0),
        'unconfirmed': address_info.get('unconfirmed_balance', 0),
        'total': address_info.get('balance', 0) + address_info.get('unconfirmed_balance', 0),
        'transaction_count': address_info.get('transaction_count', 0)
    }


def find_funding_utxo(address, min_amount=546, min_confirmations=1):
    """
    Find a suitable UTXO for funding a transaction.

    Looks for the smallest UTXO that meets minimum requirements.

    Args:
        address (str): Bitcoin address
        min_amount (int): Minimum amount in satoshis (default: 546 - dust limit)
        min_confirmations (int): Minimum confirmations (default: 1)

    Returns:
        dict or None: Best UTXO matching criteria, or None if none found

    Example:
        >>> utxo = find_funding_utxo("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", min_amount=10000)
        >>> if utxo:
        ...     print(f"Found UTXO: {utxo['txid']}:{utxo['vout']} = {utxo['value']} sats")
    """
    utxos = find_utxos(address, min_confirmations)

    # Filter by minimum amount
    valid_utxos = [u for u in utxos if u['value'] >= min_amount]

    if not valid_utxos:
        return None

    # Return smallest valid UTXO (to minimize change)
    return min(valid_utxos, key=lambda u: u['value'])


def get_recommended_fee_rate():
    """
    Get recommended fee rate from Blockchair.

    Returns:
        dict: Fee rates in satoshis per byte:
            - low: Low priority (may take hours)
            - medium: Medium priority (usually next few blocks)
            - high: High priority (likely next block)

    Example:
        >>> fees = get_recommended_fee_rate()
        >>> print(f"Medium priority: {fees['medium']} sat/byte")

    Raises:
        BlockchairError: If API request fails
    """
    url = "https://api.blockchair.com/bitcoin/stats"

    response = _make_request(url)

    if 'data' not in response:
        raise BlockchairError(f"Unexpected API response format: {response}")

    # Blockchair provides suggested fee rates
    suggested_fees = response['data'].get('suggested_transaction_fee_per_byte_sat', 10)

    # Create fee tiers (low = 50%, medium = 100%, high = 150%)
    return {
        'low': max(1, int(suggested_fees * 0.5)),
        'medium': suggested_fees,
        'high': int(suggested_fees * 1.5)
    }


# Test function
def test_blockchair():
    """
    Test Blockchair API integration.

    Note: This requires internet connection and uses a known address with balance.
    """
    print("Testing Blockchair API Integration")
    print("=" * 70)

    # Use Satoshi's address (first Bitcoin address, has many transactions)
    test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

    print(f"\nTest Address: {test_address}")

    # Test 1: Get balance
    print("\nTest 1: Get Balance")
    try:
        balance = get_address_balance(test_address)
        print(f"  Confirmed: {balance['confirmed']:,} satoshis")
        print(f"  Unconfirmed: {balance['unconfirmed']:,} satoshis")
        print(f"  Total: {balance['total']:,} satoshis")
        print(f"  Total BTC: {balance['total'] / 100000000:.8f} BTC")
    except BlockchairError as e:
        print(f"  Error: {e}")

    # Test 2: Find UTXOs
    print("\nTest 2: Find UTXOs")
    try:
        utxos = find_utxos(test_address)
        print(f"  Found {len(utxos)} UTXOs")
        for i, utxo in enumerate(utxos[:5]):  # Show first 5
            print(f"  UTXO {i+1}:")
            print(f"    TXID: {utxo['txid']}")
            print(f"    Vout: {utxo['vout']}")
            print(f"    Value: {utxo['value']:,} sats")
            print(f"    Confirmations: {utxo['confirmations']}")
        if len(utxos) > 5:
            print(f"  ... and {len(utxos) - 5} more")
    except BlockchairError as e:
        print(f"  Error: {e}")

    # Test 3: Get recommended fees
    print("\nTest 3: Get Recommended Fee Rates")
    try:
        fees = get_recommended_fee_rate()
        print(f"  Low priority: {fees['low']} sat/byte")
        print(f"  Medium priority: {fees['medium']} sat/byte")
        print(f"  High priority: {fees['high']} sat/byte")
    except BlockchairError as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 70)
    print("Blockchair API Tests Complete!")


if __name__ == "__main__":
    test_blockchair()
