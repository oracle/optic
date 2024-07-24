class Opticolor:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    STOP = "\033[0m"

    def disable_colors(self):
        self.RED = ""
        self.YELLOW = ""
        self.GREEN = ""
