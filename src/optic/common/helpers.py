def prompt_question(question: str) -> bool:
    while True:
        choice = input(f"\n{question} (Y/n): ").strip().lower()
        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        else:
            print("Please enter Y or n.")
