# ** OPTIC
# **
# ** Copyright (c) 2024 Oracle Corporation
# ** Licensed under the Universal Permissive License v 1.0
# ** as shown at https://oss.oracle.com/licenses/upl/


class OpticError(Exception):
    pass


class OpticConfigurationFileError(OpticError):
    pass


class OpticAPIError(OpticError):
    pass


class OpticDataError(OpticError):
    pass
