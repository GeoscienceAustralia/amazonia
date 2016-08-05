import logging
import yaml

logging.basicConfig(
    level=logging.INFO
)


def read_yaml(user_yaml):
    """
    Ingest user YAML
    :param user_yaml: yaml file location
    :return: Json serialised version of Yaml
    """
    with open(user_yaml, 'r') as stack_yaml:
        return yaml.safe_load(stack_yaml)
