class OpticError(Exception):
    pass


class ConfigurationFileError(OpticError):
    pass


class APIError(OpticError):
    pass


class DataError(OpticError):
    pass
