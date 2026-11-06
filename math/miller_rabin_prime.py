"""
Cryptographic Prime Generation using the Miller-Rabin test
Assigned bit length: 512

Run:  python3 miller_rabin_prime.py
"""

import secrets
import subprocess
import time

BIT_LENGTH = 512

# The "multiple bases" used in Miller-Rabin (first 20 primes).
BASES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
         31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


def miller_rabin_round(n, a):
    """One Miller-Rabin round for base a. True = 'n looks prime' for this base."""
    # Write n-1 = 2^s * d  with d odd
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1

    x = pow(a, d, n)              # a^d mod n
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)          # square it
        if x == n - 1:
            return True
    return False                  # definitely composite


def miller_rabin(n, bases=BASES):
    """Run Miller-Rabin with every base. All must pass."""
    if n < 2:
        return False
    for p in bases:               # tiny numbers / easy small factors
        if n == p:
            return True
        if n % p == 0:
            return False
    return all(miller_rabin_round(n, a) for a in bases)


def random_odd_candidate(bits):
    """Random odd number with EXACTLY `bits` bits."""
    n = secrets.randbits(bits)    # cryptographically secure random bits
    n |= (1 << (bits - 1))        # set top bit -> exactly `bits` bits long
    n |= 1                        # set last bit -> odd
    return n


def generate_prime(bits):
    """Keep generating candidates until one passes Miller-Rabin."""
    tested = 0
    while True:
        candidate = random_odd_candidate(bits)
        tested += 1
        if miller_rabin(candidate):
            return candidate, tested


def main():
    start = time.perf_counter()
    prime, tested = generate_prime(BIT_LENGTH)
    elapsed = time.perf_counter() - start

    # ---------------- Experimental results table ----------------
    results = [
        ("Assigned bit length", BIT_LENGTH),
        ("Generated prime candidate", prime),
        ("Actual bit length of the candidate", prime.bit_length()),
        ("Number of candidates tested", tested),
        ("Number of Miller-Rabin rounds", len(BASES)),
        ("Total execution time", f"{elapsed:.4f} seconds"),
    ]
    print("=" * 70)
    print("EXPERIMENTAL RESULTS")
    print("=" * 70)
    for name, value in results:
        print(f"{name}:\n    {value}\n")

    # ---------------- Verification ----------------
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    # 1. Bit length
    print(f"1) Bit length check: {prime.bit_length()} bits "
          f"(assigned {BIT_LENGTH}) -> "
          f"{'OK' if prime.bit_length() == BIT_LENGTH else 'FAIL'}")
    print(f"   Odd number check: {'OK' if prime % 2 == 1 else 'FAIL'}")

    # 2. Miller-Rabin for each base
    print("\n2) Miller-Rabin result for each base:")
    for a in BASES:
        ok = miller_rabin_round(prime, a)
        print(f"   base {a:>2}: {'PASS' if ok else 'FAIL'}")

    # 3. Independent check with a trusted library (sympy)
    print("\n3) Independent verification:")
    try:
        from sympy import isprime
        print(f"   sympy.isprime(prime) -> {isprime(prime)}")
    except ImportError:
        print("   sympy not installed (run: pip install sympy)")

    # 3b. Independent check with OpenSSL
    try:
        out = subprocess.run(["openssl", "prime", "-hex", format(prime, "x")],
                             capture_output=True, text=True, check=True)
        verdict = "PRIME" if "is prime" in out.stdout else "NOT PRIME"
        print(f"   openssl prime -hex <number> -> {verdict}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("   OpenSSL check skipped (openssl not available)")

    # Save a copy of the results
    with open("miller_rabin_results.txt", "w") as f:
        for name, value in results:
            f.write(f"{name}: {value}\n")
    print("\nResults also saved to miller_rabin_results.txt")


if __name__ == "__main__":
    main()
