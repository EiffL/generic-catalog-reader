from .BaseGalaxyCatalog import BaseGalaxyCatalog
from .GalacticusGalaxyCatalog import GalacticusGalaxyCatalog
from .BuzzardGalaxyCatalog import BuzzardGalaxyCatalog
from .AlphaQGalaxyCatalog import AlphaQGalaxyCatalog

import yaml

def load_yaml_config(yaml_config_file):
    with open(filename) as f:
        config = yaml.load(f.read())
    return config

def load_catalog(yaml_config_file):
    config = load_yaml_config(yaml_config_file)
    return locals()[config['subclass_name']](**config)
