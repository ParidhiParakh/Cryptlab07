"""
Part A: MT19937 stream cipher + brute-force of a weak 16-bit seed.
Run:  python3 part_a_stream_cipher.py
"""

import secrets
import string
import time

from mt19937_utils import mt_xor

KNOWN = b"A" * 14                               # known plaintext fragment
PRINTABLE = string.ascii_letters + string.digits + string.punctuation


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------- steps 1-2
banner("Steps 1-2: encrypt/decrypt a test message with the same function")
test_msg = b"Hello, this is a test of the MT19937 stream cipher!"
test_seed = 12345
test_ct = mt_xor(test_msg, test_seed)
test_pt = mt_xor(test_ct, test_seed)             # same function decrypts
print("Plaintext  :", test_msg)
print("Seed       :", test_seed)
print("Ciphertext :", test_ct.hex())
print("Decrypted  :", test_pt)
print("Round trip OK:", test_pt == test_msg)

# ---------------------------------------------------------------- step 3
banner("Step 3: random prefix + 14 x 'A', encrypted with a random 16-bit seed")
prefix_len = 5 + secrets.randbelow(16)           # 5..20 characters
prefix = "".join(secrets.choice(PRINTABLE) for _ in range(prefix_len)).encode()
plaintext = prefix + KNOWN
secret_seed = secrets.randbelow(2 ** 16)         # 0..65535
ciphertext = mt_xor(plaintext, secret_seed)
print("Prefix length   :", prefix_len)
print("Plaintext       :", plaintext)
print("Secret seed     :", secret_seed, "(hidden from the attacker)")
print("Ciphertext (hex):", ciphertext.hex())

# ---------------------------------------------------------------- step 4
banner("Step 4: attacker brute-forces all 65,536 seeds")
print("Attacker knows: ciphertext + the plaintext contains 14 consecutive 'A'")
start = time.perf_counter()
matches = []
for seed in range(2 ** 16):
    candidate = mt_xor(ciphertext, seed)
    if KNOWN in candidate:                       # position of the A's is unknown
        matches.append((seed, candidate))
elapsed = time.perf_counter() - start
print(f"Seeds tested    : {2 ** 16}")
print(f"Matching seeds  : {len(matches)}")
print(f"Time taken      : {elapsed:.2f} seconds")

# ---------------------------------------------------------------- step 5
banner("Step 5: verification")
if matches:
    rec_seed, rec_plain = matches[0]
    print("Recovered seed       :", rec_seed)
    print("Recovered plaintext  :", rec_plain)
    print("Seed matches secret  :", rec_seed == secret_seed)
    print("Full plaintext correct:", rec_plain == plaintext)
    print("Contains 14 x 'A'    :", KNOWN in rec_plain)
    print("Position of the A's  :", rec_plain.find(KNOWN), f"(prefix length was {prefix_len})")
else:
    print("No seed found (this should not happen).")
