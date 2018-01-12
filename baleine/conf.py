import importlib
import yaml

class Settings(object):
    def __init__(self, path):
        with open(path, 'r') as sf:
            data = yaml.load(sf)
        for key, value in data.items():
            setattr(self, key, value)

def load(path):
    global settings
    settings = Settings(path)
