# Padding Oracle Attack on AES-CBC

An educational demonstration of why **unauthenticated AES-CBC is insecure**. We
encrypt our own message with a secret key and then recover the plaintext using
nothing but a *padding oracle* — a function that leaks a single bit: whether a
decrypted ciphertext has valid PKCS#7 padding. The key is never read by the
attack.

## Background

### AES-CBC

AES is a block cipher that transforms exactly 16 bytes at a time. Cipher Block
Chaining (CBC) extends it to arbitrary-length messages by chaining blocks:

```
Encryption:  C_i = AES_encrypt(P_i XOR C_{i-1})     with C_0 = IV
Decryption:  P_i = AES_decrypt(C_i) XOR C_{i-1}      with C_0 = IV
```

Let `D_i = AES_decrypt(C_i)` be the **intermediate block** — the raw block
cipher output, *before* the XOR with the previous ciphertext block. Then:

```
P_i = D_i XOR C_{i-1}
```

### PKCS#7 padding

Messages are rarely a multiple of 16 bytes, so they are padded before
encryption. PKCS#7 appends `n` bytes, each equal to `n`:

| Bytes short | Padding appended       |
|-------------|------------------------|
| 1           | `01`                   |
| 2           | `02 02`                |
| …           | …                      |
| 0 (on boundary) | a full block `10 … 10` (sixteen `0x10` bytes) |

On decryption, the receiver reads the last byte `n`, and checks that the final
`n` bytes all equal `n`. If not, the padding is invalid.

### The padding oracle

A **padding oracle** is any system that reveals whether decryption produced
valid padding — through an error message, a timing difference, or any
observable difference in behaviour. It does **not** reveal the plaintext or the
key. That single leaked bit is enough to recover the entire message.

## Why modifying the previous ciphertext block changes the target plaintext

The attack rests entirely on the decryption identity `P_i = D_i XOR C_{i-1}`.

The attacker fully controls `C_{i-1}` — it is just ciphertext bytes they can
edit before submitting. `D_i = AES_decrypt(C_i)` depends only on the (unchanged)
target block `C_i` and the key, so it stays **fixed**. Therefore flipping a bit
in `C_{i-1}` flips exactly the corresponding bit in the decrypted plaintext
`P_i` — with no knowledge of the key.

So the attacker forges a previous block `C'` and asks the oracle whether the
result has valid padding:

1. **Last byte.** Try all 256 values of `C'[15]`. When the oracle says "valid,"
   the last plaintext byte is almost certainly `0x01`. That means
   `D_i[15] XOR C'[15] = 0x01`, so `D_i[15] = C'[15] XOR 0x01`. One intermediate
   byte recovered — without the key.
2. **Confirmation (robustness).** A hit on the last byte can be a false positive
   if the real plaintext already ends in a longer valid pad (e.g. `02 02`). We
   confirm by flipping the second-to-last forged byte and re-querying: a genuine
   `0x01` pad does not depend on that byte, so the padding must stay valid. If it
   breaks, we keep searching.
3. **Next byte.** To target `02 02`, set `C'[15] = D_i[15] XOR 0x02` (forcing the
   last byte to `0x02`), then brute-force `C'[14]` until valid → `D_i[14]`.
4. **Repeat right-to-left** for all 16 bytes to recover the whole intermediate
   block `D_i`.
5. **Recover plaintext** using the *real* previous block:
   `P_i = D_i XOR C_{i-1}`.

Repeat per block, using the IV as the previous block for the first block, then
strip the PKCS#7 padding.

## Files

| File | Purpose |
|------|---------|
| `oracle.py` | The victim: holds a private AES-128 key, `encrypt`, and the leaky `has_valid_padding`. PKCS#7 pad/unpad implemented by hand. Public `query_count`. |
| `attack.py` | `recover_block` (one block, right-to-left, with false-positive check) and `attack` (all blocks → stripped message). Uses only the oracle interface. |
| `main.py` | Demo on several messages of different lengths; verifies and prints query counts. |
| `tests/test_padding_oracle.py` | pytest: random messages of varying lengths are recovered exactly. |

## How to run

From the repository root:

```bash
pip install -r requirements.txt

# Demo
python -m modern.padding_oracle.main

# Tests
pytest modern/padding_oracle/tests/
```

Or from inside this folder:

```bash
python main.py
pytest
```

## Observed oracle query count

The work is dominated by the per-byte brute force. For each of the `16 * B`
plaintext bytes (where `B` is the number of blocks), we try up to 256 forged
values, plus a small number of confirmation probes on each block's last byte.
In practice this averages around **128 queries per byte**, i.e. roughly
`128 * 16 * B` queries overall. The worst case is bounded by `256` per byte.
`main.py` prints the exact count for each run; in the demo a two-block (32-byte)
ciphertext takes roughly **~5,000** queries, a three-block one **~6,000**, and a
five-block one **~10,000**.

## Security recommendation

The root cause is that CBC decryption acts on, and leaks information about,
**attacker-modified ciphertext before authenticating it**. Fixes:

- **Use authenticated encryption (AEAD)** such as **AES-GCM** or
  **ChaCha20-Poly1305**. Decryption fails as a single, uniform authentication
  failure before any padding is even examined, so there is no padding bit to
  leak.
- If CBC must be used, apply **Encrypt-then-MAC**: compute a MAC (e.g.
  HMAC-SHA-256) over the IV and ciphertext, and **verify it in constant time**
  *before* decrypting. Reject anything that fails the MAC, revealing nothing
  about padding.
- Never expose padding-validity results — not via distinct error messages, and
  not via timing. Distinguishable behaviour of any kind reconstitutes the
  oracle.
