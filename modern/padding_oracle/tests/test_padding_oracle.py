"""Tests that the padding oracle attack recovers plaintext exactly.

The tests encrypt random messages of varying lengths (including boundary cases
such as empty input and exact block multiples) and assert that the attack
returns the original message byte-for-byte.
"""

import os
import sys

import pytest

# Make the parent folder importable whether tests are run from the repo root or
# from inside this directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from attack import attack  # noqa: E402
from oracle import BLOCK_SIZE, PaddingOracle, pkcs7_pad, pkcs7_unpad  # noqa: E402


@pytest.mark.parametrize(
    "length",
    [
        0,   # empty -> one full padding block
        1,
        15,  # one byte short of a block
        16,  # exact block multiple -> full extra padding block
        17,
        31,
        32,  # exact multiple again
        63,
        100,
        255,
    ],
)
def test_attack_recovers_random_message(length):
    message = os.urandom(length)
    oracle = PaddingOracle()
    iv, ciphertext = oracle.encrypt(message)
    recovered = attack(iv, ciphertext, oracle)
    assert recovered == message
    assert oracle.query_count > 0


def test_attack_does_not_touch_the_key():
    """The attack must work using only the public oracle interface."""
    oracle = PaddingOracle()
    # No public attribute should expose the key.
    assert not hasattr(oracle, "key")
    iv, ciphertext = oracle.encrypt(b"no key peeking allowed")
    assert attack(iv, ciphertext, oracle) == b"no key peeking allowed"


def test_many_random_lengths():
    """A broader sweep over random lengths to catch edge cases."""
    for _ in range(25):
        length = int.from_bytes(os.urandom(1), "big")  # 0..255
        message = os.urandom(length)
        oracle = PaddingOracle()
        iv, ciphertext = oracle.encrypt(message)
        assert attack(iv, ciphertext, oracle) == message


def test_pkcs7_roundtrip_and_full_block():
    # Exact multiple gets a full extra block of 0x10 bytes.
    data = b"A" * BLOCK_SIZE
    padded = pkcs7_pad(data)
    assert len(padded) == 2 * BLOCK_SIZE
    assert padded[-BLOCK_SIZE:] == bytes([BLOCK_SIZE]) * BLOCK_SIZE
    assert pkcs7_unpad(padded) == data


def test_pkcs7_rejects_bad_padding():
    with pytest.raises(ValueError):
        pkcs7_unpad(b"A" * BLOCK_SIZE)  # last byte 'A' => invalid pad length
