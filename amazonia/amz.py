#!/usr/bin/python3

"""
Ingest User YAML and defaults YAML and send to yaml class to return as one unified data dictionary for stack input

"""
import os
import argparse
import sys
from amazonia.classes.yaml import Yaml
from amazonia.classes.stack import Stack
from amazonia.classes.util import read_yaml


def create_stack(united_data):
    """
    Create Stack using amazonia
    :param united_data: Dictionary of yaml consisting of user yaml values with default yaml values for any missing keys
    return: Troposphere template object
    """

    stack = Stack(**united_data)

    return stack


def generate_template(yaml_data, default_data):
    """
    Generate troposhere template from given yaml data
    :param yaml_data: User yaml data
    :param default_data: default yaml data
    :return: Troposphere generated cloud formation template
    """
    yaml_return = Yaml(yaml_data, default_data)
    stack_input = yaml_return.united_data

    # Create stack and create stack template file
    template_trop = create_stack(stack_input)
    template_data = template_trop.template.to_json(indent=2, separators=(',', ': '))
    return template_data


def main():
    """
    Ingest User YAML as user_stack_data
    Ingest default YAML as default_data
    Create list of stack input dictoinary objects from yaml class
    Create stack from stack input dictionary
    Create Stack template from stack output
    """

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--yaml',
                        default=os.path.join(__location__, 'application.yaml'),
                        help="Path to the applications amazonia yaml file")
    parser.add_argument('-d', '--default',
                        default=os.path.join(__location__, './defaults.yaml'),
                        help='Path to the environmental defaults yaml file')
    parser.add_argument('-t', '--template',
                        default='stack.template',
                        help='Path for amazonia to place template file')
    parser.add_argument('-o', '--out',
                        action='store_true',
                        help='Output template to stdout rather than a file.')
    args = parser.parse_args()

    # YAML ingestion
    user_stack_data = read_yaml(args.yaml)
    default_data = read_yaml(args.default)

    # Create stack and create stack template file
    template_file_path = args.template
    send_to_output = args.out

    template_data = generate_template(user_stack_data, default_data)

    if send_to_output is True:
        sys.stdout.write(template_data)
    else:
        with open(template_file_path, 'w') as template_file:
            template_file.write(template_data)
            template_file.close()
        print('Amazonia has successfully created stack template at location: {0}'.format(template_file_path))

if __name__ == '__main__':
    main()
