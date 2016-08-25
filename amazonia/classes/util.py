import logging
import re

import yaml

logging.basicConfig(
    level=logging.INFO
)


def get_cf_friendly_name(object_name):
    return re.sub(r'\W+', '', object_name)


def read_yaml(user_yaml):
    """
    Load and return data from userdefined yaml file
    :param user_yaml: yaml file location
    :return: Json serialised version of Yaml
    """
    with open(user_yaml, 'r') as stack_yaml:
        return yaml.safe_load(stack_yaml)
