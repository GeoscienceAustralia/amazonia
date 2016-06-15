#!/usr/bin/python3

import yaml
import os
from amazonia.classes.yaml import Yaml


def main():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, '../../amazonia/application.yaml'), 'r') as stack_yaml:
        user_stack_data = yaml.safe_load(stack_yaml)
        print('\nuser_stack_data=\n{0}\n'.format(user_stack_data))

    with open(os.path.join(__location__, '../../amazonia/defaults.yaml'), 'r') as default_yaml:
        default_data = yaml.safe_load(default_yaml)
        print('\ndefault_data=\n{0}\n'.format(default_data))

    with open(os.path.join(__location__, '../../amazonia/schema.yaml'), 'r') as schema_yaml:
        schema = yaml.safe_load(schema_yaml)
        print('\nschema=\n{0}\n'.format(schema))

    yaml_return = Yaml(user_stack_data, default_data, schema)
    stack_input = yaml_return.united_data

    print('\nstack_input=\n{0}\n'.format(stack_input))


if __name__ == '__main__':
    main()
