def prompt_question(question: str, default_response: bool = False) -> bool:
    """
    Prompts the user with a es or no question and returns their response as a boolean.

    The function will continue to prompt the user until a valid response is given.
    A valid response is either 'y', 'yes', 'n', or 'no' (case-insensitive).
    If the user presses Enter without any input, the default value is returned.

    Args:
    question (str): The question to be asked to the user.
    default_response (bool): The default value to return if the user presses Enter.
                             Defaults to False.

    Returns:
    bool: The user's response to the question.
    """
    while True:
        choices = {
            True: "[Y/n]",
            False: "[y/N]",
        }
        choice = (
            input(f"\n{question} {choices.get(default_response)}: ").strip().lower()
        )
        if choice == "":
            return default_response
        elif choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n' (case-insensitive).")
