"""AES-CBC padding oracle target.

This module provides the *victim* side of the exercise: it holds a secret AES
key, encrypts messages with AES-128 in CBC mode using PKCS#7 padding, and
exposes a single leaky method -- ``has_valid_padding`` -- that reveals one bit
of information: whether a decrypted ciphertext ends in valid PKCS#7 padding.

The attack code (see ``attack.py``) is only allowed to call ``encrypt`` to
obtain a challenge ciphertext and ``has_valid_padding`` as the oracle. It must
never read the key or any private attribute.

PKCS#7 padding/unpadding is implemented by hand (rather than using the
library's padding helpers) so that the validity logic is fully explicit and
auditable.
"""

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK_SIZE = 16  # AES block size in bytes (AES-128 => 16-byte blocks).


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Append PKCS#7 padding so the result is a multiple of ``block_size``.

    The number of padding bytes ``n`` (1..block_size) is appended, each byte
    having the value ``n``. When ``data`` is already a multiple of the block
    size, a full extra block of ``block_size`` bytes is added, so that
    unpadding is always unambiguous.
    """
    pad_len = block_size - (len(data) % block_size)
    # pad_len is in 1..block_size: it is never 0, which is what forces a full
    # extra block when the input already ends on a block boundary.
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Strip and validate PKCS#7 padding, returning the original message.

    Raises ``ValueError`` if the padding is malformed. This is the exact check
    the oracle relies on.
    """
    if not data or len(data) % block_size != 0:
        raise ValueError("invalid data length for PKCS#7")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("invalid PKCS#7 padding length")
    # Every one of the last ``pad_len`` bytes must equal pad_len.
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("invalid PKCS#7 padding bytes")
    return data[:-pad_len]


class PaddingOracle:
    """An AES-128-CBC encryptor that leaks PKCS#7 padding validity.

    The secret key is generated on construction and never exposed. The only
    methods an attacker is meant to use are :meth:`encrypt` (to get a
    challenge) and :meth:`has_valid_padding` (the oracle).
    """

    def __init__(self) -> None:
        # The key is private: stored under a name-mangled attribute and never
        # returned by any method. The attack must succeed without it.
        self.__key = os.urandom(BLOCK_SIZE)
        # Public counter: the number of oracle queries made so far. The attack
        # analysis reports this value.
        self.query_count = 0

    def encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        """PKCS#7-pad then AES-CBC-encrypt ``plaintext``.

        Returns ``(iv, ciphertext)`` with a fresh random IV each call.
        """
        iv = os.urandom(BLOCK_SIZE)
        padded = pkcs7_pad(plaintext)
        encryptor = Cipher(algorithms.AES(self.__key), modes.CBC(iv)).encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        return iv, ciphertext

    def has_valid_padding(self, iv: bytes, ciphertext: bytes) -> bool:
        """The padding oracle: decrypt and report whether padding is valid.

        This is the ONLY information leak the attacker is allowed to use. It
        returns ``True`` iff the AES-CBC decryption of ``ciphertext`` (under the
        given ``iv``) carries valid PKCS#7 padding. Every call increments the
        public ``query_count``.
        """
        self.query_count += 1
        decryptor = Cipher(algorithms.AES(self.__key), modes.CBC(iv)).decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        try:
            pkcs7_unpad(plaintext)
            return True
        except ValueError:
            return False
