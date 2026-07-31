from analysis.file_analysis import analyze_file
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
        elif choice == "2":
            print("Decrypt -> Coming Soon")
        elif choice == "3":
            print("Attack -> Coming Soon")
        elif choice == "4":
            analyze()
        elif choice == "5":
            print("Exiting CryptoLabX. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
 
 
if __name__ == "__main__":
    main()
