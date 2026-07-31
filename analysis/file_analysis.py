import os
from collections import Counter

DATASET_FOLDER = "datasets"

def analyze_file(filename):
    filepath = os.path.join(DATASET_FOLDER, filename)

    if not os.path.exists(filepath):
        print("File not found.")
        return

    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()

    characters = len(text)
    words = len(text.split())
    lines = len(text.splitlines())
    unique_characters = len(set(text))

    # Count only alphabetic letters (case-insensitive)
    letters = [char.lower() for char in text if char.isalpha()]
    frequency = Counter(letters)

    print("\n----- File Analysis -----")
    print(f"Characters       : {characters}")
    print(f"Words            : {words}")
    print(f"Lines            : {lines}")
    print(f"Unique Characters: {unique_characters}")

    print("\nLetter Frequency:")
    for letter in sorted(frequency):
        print(f"{letter} : {frequency[letter]}")
