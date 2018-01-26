import yaml

class Settings(object):
    """ Simple object that holds global configuration data """

    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

def load(path):
    """ Load configuration from a yaml file """
    global settings
    with open(path, 'r') as sf:
        data = yaml.load(sf)
    settings = Settings(data)
