#!/usr/bin/python3

import yaml
import os
from amazonia.classes.yaml import Yaml


def main():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'amazonia.yaml'), 'r') as stack_yaml:
        user_stack_data = yaml.safe_load(stack_yaml)
        print('\nuser_stack_data=\n{0}\n'.format(user_stack_data))

    with open(os.path.join(__location__, '../../amazonia/amazonia_ga_defaults.yaml'), 'r') as default_yaml:
        default_data = yaml.safe_load(default_yaml)
        print('\ndefault_data=\n{0}\n'.format(default_data))

    yaml_return = Yaml(user_stack_data, default_data)
    stack_input = yaml_return.united_data

    print('\nstack_input=\n{0}\n'.format(stack_input))


if __name__ == "__main__":
    main()
