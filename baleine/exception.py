
class BusyError(RuntimeError):
    """ A requested resource is busy at the moment """
    pass

class ConfigurationError(RuntimeError):
    """ Some configuration file is incorrect """
    pass

class PermissionDenied(RuntimeError):
    """ An attempted operation was forbidden """
    pass
