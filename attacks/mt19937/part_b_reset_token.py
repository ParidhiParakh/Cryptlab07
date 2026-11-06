"""
Part B: predictable password-reset tokens (MT19937 seeded with the Unix time).
Run:  python3 part_b_reset_token.py
"""

import json
import time
from pathlib import Path

from mt19937_utils import make_token

WINDOW = 300                                      # attacker searches +/- 300 seconds


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------- steps 6-8
banner("Steps 6-8: server generates a reset token")
T = int(time.time())                              # step 6: timestamp in Unix seconds
token = make_token(T)                             # step 7: 16 MT19937 outputs -> 16 bytes
print("Timestamp T      :", T)
print("Token (hex)      :", token.hex())
print("Token length     :", len(token), "bytes")

out_dir = Path(__file__).resolve().parents[2] / "outputs"
out_dir.mkdir(exist_ok=True)
(out_dir / "reset_token.json").write_text(
    json.dumps({"timestamp": T, "token_hex": token.hex()}, indent=2))
print("Saved to         :", out_dir / "reset_token.json")

# ---------------------------------------------------------------- steps 9-11
banner("Steps 9-11: attacker predicts the timestamp")
print("The attacker sees the token a little later and does NOT know T.")
time.sleep(2)
now = int(time.time())                            # attacker's own clock
low, high = now - WINDOW, now + WINDOW
print(f"Search interval  : {low} to {high}  (now +/- {WINDOW} seconds)")

tested = 0
found = []
for candidate_T in range(low, high + 1):
    tested += 1
    if make_token(candidate_T) == token:
        found.append(candidate_T)

print("Timestamps tested:", tested)
print("Matching times   :", found)

# verification
banner("Verification")
if found:
    rec_T = found[0]
    regenerated = make_token(rec_T)
    print("Recovered timestamp :", rec_T)
    print("Regenerated token   :", regenerated.hex())
    print("Observed token      :", token.hex())
    print("Tokens match        :", regenerated == token)
    print("Equals real T       :", rec_T == T)
else:
    print("No match in the interval (generation was outside the window).")
