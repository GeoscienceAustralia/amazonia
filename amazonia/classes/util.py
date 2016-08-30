import logging
import re

import yaml

logging.basicConfig(
    level=logging.INFO
)


def get_cf_friendly_name(resource_name):
    """
    Strip non cloud formation friendly characters from a cloud formation resource name
    :param resource_name: input name, potentially containing unfriendly characters like spaces, dashes, underscores etc
    :return: return clean string
    """
    return re.sub(r'\W+', '', resource_name)


def read_yaml(user_yaml):
    """
    Load and return data from userdefined yaml file
    :param user_yaml: yaml file location
    :return: Json serialised version of Yaml
    """
    with open(user_yaml, 'r') as stack_yaml:
        return yaml.safe_load(stack_yaml)


def detect_unencrypted_access_keys(userdata):
    """
    Searches userdata for potential AWS access ids and secret keys and substitutes entire userdata with error string
    :param userdata: Userdata for each unit in the stack
    """
    aws_access_id = re.compile('(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])')
    aws_secret_key = re.compile('(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])')

    if aws_access_id.search(userdata):
        raise InsecureVariableError('Error: unencrypted {0} was found in your userdata, please remove or encrypt.'
                                    .format('AWS access ID'))
    elif aws_secret_key.search(userdata):
        raise InsecureVariableError('Error: unencrypted {0} was found in your userdata, please remove or encrypt.'
                                    .format('AWS secret Key'))


class InsecureVariableError(Exception):
    """
    Exception if aws access ud ir aws secret key is detected in userdata
    """
    def __init__(self, value):
        self.value = value
