# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/


class OpticColor:
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    STOP = "\033[0m"
    YELLOW = "\033[93m"

    ERROR = RED + BOLD
    OK_CYAN = CYAN + BOLD
    OK_GREEN = GREEN + BOLD
    WARNING = YELLOW + BOLD

    def disable_colors(self) -> None:
        """
        Makes OpticColor disable all colors

        :return: None
        :rtype: None
        """
        for attr, value in self.__dict__.items():
            if (
                isinstance(value, str)
                and value.startswith("\033[")
                and value.endswith("m")
            ):
                setattr(self, attr, "")
