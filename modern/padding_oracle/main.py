"""Demo driver for the AES-CBC padding oracle attack.

Encrypts sample messages with the oracle, runs the attack using only the public
oracle interface, prints the recovered plaintext, verifies it matches the
original, and reports how many oracle queries were required.

Run from the repository root:

    python -m modern.padding_oracle.main

or from inside this folder:

    python main.py
"""

try:
    # When run as a package module: python -m modern.padding_oracle.main
    from .oracle import PaddingOracle
    from .attack import attack
except ImportError:
    # When run directly: python main.py
    from oracle import PaddingOracle
    from attack import attack


def run_demo(label: str, message: bytes) -> None:
    """Encrypt ``message``, attack it, and report the result."""
    oracle = PaddingOracle()
    start_count = oracle.query_count

    iv, ciphertext = oracle.encrypt(message)
    recovered = attack(iv, ciphertext, oracle)

    queries = oracle.query_count - start_count
    blocks = len(ciphertext) // 16

    print(f"=== {label} ===")
    print(f"  original length : {len(message)} bytes")
    print(f"  ciphertext      : {blocks} blocks ({len(ciphertext)} bytes, padded)")
    print(f"  recovered       : {recovered!r}")
    assert recovered == message, "recovered plaintext does not match original!"
    print("  match           : OK")
    print(f"  oracle queries  : {queries}")
    print()


def main() -> None:
    # A multi-block message. 29 bytes pads into 2 full 16-byte blocks (32).
    run_demo(
        "message spanning several blocks",
        b"Attack at dawn, bring coffee.",
    )

    # A message whose length is an exact multiple of 16, which forces a full
    # extra 16-byte padding block (0x10 * 16). Here 32 bytes -> 48 bytes.
    run_demo(
        "length is a multiple of 16 (full padding block)",
        b"EXACTLY-THIRTY-TWO-BYTES-LONG!!!",
    )

    # A different length again, to show the attack is generic, not tuned to a
    # particular message or size.
    run_demo(
        "a longer, different-length message",
        b"Padding oracles turn one leaked bit into full plaintext recovery.",
    )


if __name__ == "__main__":
    main()
