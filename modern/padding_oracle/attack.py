"""Padding oracle attack against AES-CBC.

The attack recovers the plaintext of a CBC ciphertext using *only* the oracle's
``has_valid_padding`` method and the public ``(iv, ciphertext)``. It never reads
the key or any private attribute of the oracle.

Core identity (CBC decryption):

    P_i = AES_decrypt(C_i) XOR C_{i-1}        (C_0 = IV)

Let ``D_i = AES_decrypt(C_i)`` be the *intermediate* block -- the raw block
cipher output, before the XOR. Since the attacker controls the previous block
sent to the oracle, forging a byte ``g`` in position ``j`` makes the decrypted
byte at that position equal ``D_i[j] XOR g``. By searching for the ``g`` that
produces valid PKCS#7 padding, we learn ``D_i[j]`` -- all without the key.
Once ``D_i`` is known, the real plaintext is ``D_i XOR C_{i-1}``.
"""

BLOCK_SIZE = 16


def recover_block(prev_block: bytes, target_block: bytes, oracle) -> bytes:
    """Recover the 16-byte plaintext of ``target_block``.

    ``prev_block`` is the real preceding ciphertext block (the IV for the first
    block). We recover the intermediate bytes ``D_i`` of ``target_block``
    right-to-left by forging a synthetic previous block, then XOR with the real
    ``prev_block`` to obtain the plaintext.
    """
    intermediate = bytearray(BLOCK_SIZE)  # D_i, filled right-to-left.

    # pad_len counts how many trailing bytes we are currently forcing to a
    # known padding value. We go from 1 (last byte) up to BLOCK_SIZE.
    for pad_len in range(1, BLOCK_SIZE + 1):
        pos = BLOCK_SIZE - pad_len  # index of the byte we are solving now.

        # Build the forged previous block. For every already-recovered byte to
        # the right of ``pos`` we set the forged byte so that the decrypted
        # plaintext byte equals ``pad_len`` (the padding value we want).
        forged = bytearray(BLOCK_SIZE)
        for k in range(pos + 1, BLOCK_SIZE):
            forged[k] = intermediate[k] ^ pad_len

        found = False
        for guess in range(256):
            forged[pos] = guess
            if not oracle.has_valid_padding(bytes(forged), target_block):
                continue

            # Oracle says padding is valid. For the LAST byte (pad_len == 1)
            # this might be a false positive: the plaintext may already end in
            # a longer valid pad (e.g. a real 0x02 0x02). Confirm by perturbing
            # the second-to-last byte; a genuine 0x01 pad does not depend on it,
            # so padding must stay valid.
            if pad_len == 1 and pos - 1 >= 0:
                probe = bytearray(forged)
                probe[pos - 1] ^= 0xFF  # flip the byte to its left.
                if not oracle.has_valid_padding(bytes(probe), target_block):
                    # Padding broke => the hit relied on a longer pad, not 0x01.
                    continue

            # D_i[pos] XOR guess == pad_len  =>  D_i[pos] = guess XOR pad_len.
            intermediate[pos] = guess ^ pad_len
            found = True
            break

        if not found:
            raise RuntimeError(
                f"padding oracle: no valid byte found at position {pos}"
            )

    # Real plaintext = intermediate XOR real previous block.
    return bytes(intermediate[i] ^ prev_block[i] for i in range(BLOCK_SIZE))


def attack(iv: bytes, ciphertext: bytes, oracle) -> bytes:
    """Recover the full plaintext message from ``(iv, ciphertext)``.

    Iterates over every ciphertext block, using the preceding ciphertext block
    (the IV for the first block) as the previous block, recovers the padded
    plaintext, then strips PKCS#7 padding and returns the original message.
    """
    if len(ciphertext) == 0 or len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("ciphertext must be a non-empty multiple of the block size")

    # All blocks in order, with the IV prepended so that blocks[i] is the
    # previous block of blocks[i+1].
    blocks = [iv] + [
        ciphertext[i : i + BLOCK_SIZE]
        for i in range(0, len(ciphertext), BLOCK_SIZE)
    ]

    recovered = bytearray()
    for i in range(1, len(blocks)):
        recovered += recover_block(blocks[i - 1], blocks[i], oracle)

    return _pkcs7_strip(recovered)


def _pkcs7_strip(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Strip PKCS#7 padding from fully recovered plaintext.

    Implemented here (rather than importing the oracle's helper) so the attack
    stands on its own and relies on nothing but the oracle interface.
    """
    if not data or len(data) % block_size != 0:
        raise ValueError("recovered plaintext has invalid length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("recovered plaintext has invalid padding")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("recovered plaintext has invalid padding")
    return bytes(data[:-pad_len])
