import os
import yaml
import cerberus
import pprint

def open_yaml_file(file_path):
    """
    Open yaml file and return dictionary of values
    :param file_path: file path to yaml file
    :return: dictionary of values from yaml file
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, file_path), 'r') as input_yaml:
        return yaml.safe_load(input_yaml)

def main():
    schema = open_yaml_file('../../amazonia/schemas/cerberus_schema.yaml')
    data = open_yaml_file('../../amazonia/defaults.yaml')
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(schema)

    validator = cerberus.Validator()

    validator.validate(data, schema)


if __name__ == '__main__':
    main()
