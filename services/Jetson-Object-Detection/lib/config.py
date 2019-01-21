import os
import yaml


def load_config():
    """Load config params."""
    if os.path.isfile('config.yml'):
        with open("config.yml", 'r') as ymlfile:
            config = yaml.load(ymlfile)
    else:
        with open("config.sample.yml", 'r') as ymlfile:
            config = yaml.load(ymlfile)

    return config
