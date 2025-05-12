def prompt_question(question: str, default: bool = False) -> bool:
    while True:
        choices = {
            True: "[Y/n]",
            False: "[y/N]",
        }
        choice = input(f"\n{question} {choices.get(default)}: ").strip().lower()
        if choice == "":
            return default
        elif choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n' (case-insensitive).")
