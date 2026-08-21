# Shift Cipher Cryptanalysis

Cryptanalysis of the classical Shift Cipher (Caesar Cipher) using two
independent approaches:

1. **Brute-Force + Dictionary Scoring** (`src/brute_force_dictionary.py`)
   Tries all 26 keys and scores each candidate plaintext by how many
   of its words appear in a large English dictionary. The key with
   the highest word-match count wins.

2. **Chi-Square Statistical Attack** (`src/chi_square_attack.py`)
   Tries all 26 keys and compares each candidate's letter-frequency
   distribution against the known English letter-frequency
   distribution using the chi-square statistic. The key with the
   lowest chi-square value (closest fit to English) wins.

## Project layout

```
shift_cipher_attack/
├── src/
│   ├── shift_cipher.py            # Encrypt / decrypt
│   ├── brute_force_dictionary.py  # Attack 1
│   ├── chi_square_attack.py       # Attack 2
│   └── main.py                    # Runs the test suite / a single ciphertext
├── dictionary/
│   └── english_words.txt          # ~102k word English dictionary (from wamerican)
├── testcases/
│   └── testcases.json             # Plaintext + key definitions for the test suite
├── outputs/
│   ├── results_table.csv          # Summary table (all test cases)
│   └── <test_id>_detail.txt       # Full 26-key breakdown per test case
├── screenshots/
├── reports/
│   └── Assignment_4_Report.pdf
└── README.md
```

## Usage

Run the full test suite (reads `testcases/testcases.json`, writes to `outputs/`):

```bash
cd src
python3 main.py
```

Attack a single, arbitrary ciphertext instead:

```bash
python3 main.py --ciphertext "Wklv lv d whvw phvvdjh"
```

Run either attack module standalone (each has a small built-in demo):

```bash
python3 shift_cipher.py
python3 brute_force_dictionary.py
python3 chi_square_attack.py
```

## Results table format

| Test Case | Actual Key | Dictionary Key | Chi-Square Key | Dictionary Correct? | Chi-Square Correct? |
|---|---|---|---|---|---|

`outputs/results_table.csv` is generated in exactly this format after
running `main.py`.

## Notes

- The dictionary (`dictionary/english_words.txt`) was generated from
  the standard Debian/Ubuntu `wamerican` word list package, filtered
  to lowercase alphabetic entries only.
- `testcases/testcases.json` intentionally includes a short/edge-case
  test (`TC6_single_word`) alongside normal sentences, since comparing
  where each attack succeeds or fails is part of the lab analysis.
