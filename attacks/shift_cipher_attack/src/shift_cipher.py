"""
shift_cipher.py

Implements the classical Shift Cipher (a.k.a. Caesar Cipher) over the
26-letter English alphabet.

Encryption:  C = (P + k) mod 26
Decryption:  P = (C - k) mod 26

where P and C are the 0-25 index of a letter in the alphabet and k is
the secret key (0-25).

Only alphabetic characters are shifted. Letter case is preserved.
All other characters (spaces, digits, punctuation) pass through
unchanged, since the shift operation is only defined over letters.
"""

from typing import Final

ALPHABET_SIZE: Final[int] = 26


def _shift_char(ch: str, key: int) -> str:
    """Shift a single character by `key` positions (mod 26)."""
    if ch.isupper():
        base = ord('A')
    elif ch.islower():
        base = ord('a')
    else:
        return ch  # non-alphabetic characters are left untouched
    return chr((ord(ch) - base + key) % ALPHABET_SIZE + base)


def encrypt(plaintext: str, key: int) -> str:
    """Encrypt `plaintext` with the given shift `key` (0-25)."""
    key %= ALPHABET_SIZE
    return ''.join(_shift_char(ch, key) for ch in plaintext)


def decrypt(ciphertext: str, key: int) -> str:
    """Decrypt `ciphertext` that was encrypted with the given shift `key`."""
    key %= ALPHABET_SIZE
    return ''.join(_shift_char(ch, -key) for ch in ciphertext)


if __name__ == "__main__":
    # Quick manual sanity check
    pt = "Attack at dawn"
    k = 5
    ct = encrypt(pt, k)
    print(f"Plaintext : {pt}")
    print(f"Key       : {k}")
    print(f"Ciphertext: {ct}")
    print(f"Decrypted : {decrypt(ct, k)}")
    assert decrypt(ct, k) == pt, "encrypt/decrypt round trip failed!"
    print("Round-trip check passed.")
