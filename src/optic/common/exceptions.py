class OpticError(Exception):
    pass


class OpticConfigurationFileError(OpticError):
    pass


class OpticAPIError(OpticError):
    pass


class OpticDataError(OpticError):
    pass
