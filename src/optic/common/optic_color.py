# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/


class OpticColor:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    STOP = "\033[0m"

    def disable_colors(self) -> None:
        """
        Makes OpticColor disable all colors

        :return: None
        :rtype: None
        """
        self.RED = ""
        self.YELLOW = ""
        self.GREEN = ""
