"""
Shared helpers for the MT19937 lab (used by Part A and Part B).

We use Python's built-in `random.Random`, which is an MT19937 generator.
Byte-extraction procedure (used EVERYWHERE in this lab):
    one 8-bit value = rng.getrandbits(8)
    (CPython takes one 32-bit MT19937 output and keeps its top 8 bits)
"""

import random


def keystream_byte(rng):
    """Next 8-bit keystream value from an MT19937 generator."""
    return rng.getrandbits(8)


def mt_xor(data: bytes, seed: int) -> bytes:
    """Stream cipher: XOR data with an MT19937 keystream.
    The SAME function encrypts and decrypts (XOR twice gives the original)."""
    rng = random.Random(seed)                 # MT19937 seeded with `seed`
    return bytes(b ^ keystream_byte(rng) for b in data)


def make_token(timestamp: int, length: int = 16) -> bytes:
    """Reset token: `length` consecutive 8-bit MT19937 outputs, seeded with a timestamp."""
    rng = random.Random(timestamp)
    return bytes(keystream_byte(rng) for _ in range(length))
