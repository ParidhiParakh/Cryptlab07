import os
from datetime import datetime
from analysis.file_analysis import analyze_file

def log_action(choice_text):
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("outputs/execution_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - Selected: {choice_text}\n")


def show_menu():
    """
    Prints the menu options to the screen.
    """
    print("\n===== CryptoLabX Menu =====")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Attack")
    print("4. Analyze")
    print("5. Exit")
 
 
def main():
    """
    This is the "engine" of the program: it keeps showing the menu and
    reacting to the user's choice until they choose to exit.
    """
    def analyze():
    filename = input("Enter filename (example: sample1.txt): ")
    analyze_file(filename)
    while True:
        show_menu()
 
        # .strip() removes any accidental spaces the user might type.
        choice = input("Enter your choice (1-5): ").strip()
 
        if choice == "1":
            print("Encrypt -> Coming Soon")
            log_action("Encrypt")
        elif choice == "2":
            print("Decrypt -> Coming Soon")
            log_action("Decrypt")
        elif choice == "3":
            print("Attack -> Coming Soon")
            log_action("Attack")
        elif choice == "4":
            print("Analyze -> Coming Soon")
            log_action("Analyze")
        elif choice == "5":
            print("Exiting CryptoLabX. Goodbye!")
            log_action("Exit")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
 
 
if __name__ == "__main__":
    main()
