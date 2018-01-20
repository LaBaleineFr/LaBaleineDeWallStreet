
class BusyError(RuntimeError):
    """ A requested resource is busy at the moment """
    pass

class ConfigurationError(RuntimeError):
    pass

class PermissionDenied(RuntimeError):
    pass
