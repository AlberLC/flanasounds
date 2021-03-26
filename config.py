import configparser

from utils import resource_path


class Config(configparser.ConfigParser):
    def __init__(self, path):
        super().__init__(interpolation=configparser.ExtendedInterpolation(),
                         allow_no_value=False)
        self.path = path

        self.read(self.path)

    def save(self):
        with open(self.path, 'w') as file:
            self.write(file)


config = Config('config.ini')

resources = config['resources']
settings = config['settings']
volume = config['volume']
