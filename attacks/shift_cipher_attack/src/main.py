"""
main.py

Driver script for the Shift Cipher cryptanalysis lab.

For every test case (defined in testcases/testcases.json) this script:
    1. Encrypts the known plaintext with the known key -> ciphertext.
    2. Runs the Brute-Force + Dictionary Scoring attack on the
       ciphertext to predict a key.
    3. Runs the Chi-Square attack on the same ciphertext to predict
       a (possibly different) key.
    4. Records whether each attack's predicted key matches the
       actual key.
    5. Prints/saves a results table in the format required by the
       lab notebook:

        Test Case | Actual Key | Dictionary Key | Chi-Square Key |
        Dictionary Correct? | Chi-Square Correct?

Usage
-----
    Run the full test suite (default):
        python main.py

    Attack a single arbitrary ciphertext instead of the test suite:
        python main.py --ciphertext "Wklv lv d whvw phvvdjh"

Outputs
-------
    outputs/results_table.csv   - the summary table (also printed)
    outputs/<test_id>_detail.txt - per-test-case detail: ciphertext,
                                   full 26-key candidate list from
                                   both attacks, and scores.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from shift_cipher import encrypt
from brute_force_dictionary import brute_force_dictionary_attack, load_dictionary
from chi_square_attack import chi_square_attack

SRC_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SRC_DIR.parent
TESTCASES_PATH = PROJECT_DIR / "testcases" / "testcases.json"
OUTPUTS_DIR = PROJECT_DIR / "outputs"


def load_testcases(path: Path = TESTCASES_PATH) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_single_attack(ciphertext: str, dictionary) -> Dict[str, Any]:
    """Run both attacks on one ciphertext and return everything needed
    for the results table and the per-test detail report."""
    dict_key, dict_scores, dict_candidates = brute_force_dictionary_attack(
        ciphertext, dictionary
    )
    chi_key, chi_scores, chi_candidates = chi_square_attack(ciphertext)

    return {
        "dict_key": dict_key,
        "dict_scores": dict_scores,
        "dict_candidates": dict_candidates,
        "chi_key": chi_key,
        "chi_scores": chi_scores,
        "chi_candidates": chi_candidates,
    }


def write_detail_report(test_id: str, plaintext: str, actual_key: int,
                         ciphertext: str, result: Dict[str, Any]) -> Path:
    """Write a full per-test-case report with all 26 candidate keys,
    useful for screenshots and for the Failure Analysis section."""
    out_path = OUTPUTS_DIR / f"{test_id}_detail.txt"
    lines = []
    lines.append(f"Test Case      : {test_id}")
    lines.append(f"Plaintext      : {plaintext}")
    lines.append(f"Actual Key     : {actual_key}")
    lines.append(f"Ciphertext     : {ciphertext}")
    lines.append("")
    lines.append(f"Dictionary attack predicted key : {result['dict_key']}"
                  f"  ({'CORRECT' if result['dict_key'] == actual_key else 'WRONG'})")
    lines.append(f"Chi-Square attack predicted key  : {result['chi_key']}"
                  f"  ({'CORRECT' if result['chi_key'] == actual_key else 'WRONG'})")
    lines.append("")
    lines.append("Key | Dict Score | Chi-Square | Candidate Plaintext")
    lines.append("-" * 90)
    for k in range(26):
        lines.append(
            f"{k:3d} | {result['dict_scores'][k]:10d} | "
            f"{result['chi_scores'][k]:10.2f} | {result['dict_candidates'][k]}"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def print_and_save_table(rows: List[Dict[str, Any]]) -> None:
    headers = [
        "Test Case", "Actual Key", "Dictionary Key", "Chi-Square Key",
        "Dictionary Correct?", "Chi-Square Correct?",
    ]

    col_widths = [max(len(str(row[h])) for row in rows + [dict(zip(headers, headers))])
                  for h in headers]
    # Ensure at least header width
    col_widths = [max(w, len(h)) for w, h in zip(col_widths, headers)]

    def fmt_row(values):
        return " | ".join(str(v).ljust(w) for v, w in zip(values, col_widths))

    print(fmt_row(headers))
    print("-+-".join("-" * w for w in col_widths))
    for row in rows:
        print(fmt_row([row[h] for h in headers]))

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUTS_DIR / "results_table.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row[h] for h in headers})
    print(f"\nSaved results table -> {csv_path}")


def run_test_suite() -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    dictionary = load_dictionary()
    testcases = load_testcases()

    rows = []
    for tc in testcases:
        plaintext = tc["plaintext"]
        actual_key = tc["key"]
        ciphertext = encrypt(plaintext, actual_key)

        result = run_single_attack(ciphertext, dictionary)
        write_detail_report(tc["id"], plaintext, actual_key, ciphertext, result)

        rows.append({
            "Test Case": tc["id"],
            "Actual Key": actual_key,
            "Dictionary Key": result["dict_key"],
            "Chi-Square Key": result["chi_key"],
            "Dictionary Correct?": "Yes" if result["dict_key"] == actual_key else "No",
            "Chi-Square Correct?": "Yes" if result["chi_key"] == actual_key else "No",
        })

    print_and_save_table(rows)


def run_single_ciphertext(ciphertext: str) -> None:
    dictionary = load_dictionary()
    result = run_single_attack(ciphertext, dictionary)

    print(f"Ciphertext                 : {ciphertext}")
    print(f"Dictionary attack -> key   : {result['dict_key']}  "
          f"-> {result['dict_candidates'][result['dict_key']]!r}")
    print(f"Chi-Square attack -> key   : {result['chi_key']}  "
          f"-> {result['chi_candidates'][result['chi_key']]!r}")

    if result["dict_key"] != result["chi_key"]:
        print("\nNote: the two attacks disagree on the predicted key. "
              "Inspect the per-key scores above/below to judge which is "
              "more plausible English.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Shift Cipher cryptanalysis: brute-force+dictionary vs chi-square."
    )
    parser.add_argument(
        "--ciphertext", type=str, default=None,
        help="Attack a single arbitrary ciphertext instead of running the test suite.",
    )
    args = parser.parse_args()

    if args.ciphertext is not None:
        run_single_ciphertext(args.ciphertext)
    else:
        run_test_suite()


if __name__ == "__main__":
    main()
