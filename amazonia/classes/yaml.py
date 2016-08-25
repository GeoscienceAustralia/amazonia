#!/usr/bin/python3
"""
Ingest User YAML and defaults YAML
Overwrite defaults YAML with User YAML
"""
import os

import cerberus
from amazonia.classes.util import read_yaml
from amazonia.classes.yaml_fields import YamlFields


class Yaml(object):
    """
    Setting these as class variables rather than instance variables so that they can be resolved and referred to
    statically
    """

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    """ cerberus schema file location """
    cerberus_schema = read_yaml(os.path.join(__location__, '../schemas/cerberus_schema.yaml'))

    def __init__(self, user_stack_data, default_data):
        """
        Initializes united, user and default data dictionaries
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()

        # Validate user and default yaml against the provided schema before attempting to combine them.
        self.validate_yaml(self.user_stack_data, self.cerberus_schema)
        self.validate_yaml(self.default_data, self.cerberus_schema)

        for stack_key in YamlFields.stack_key_list:
            self.united_data[stack_key] = self.set_value(stack_key, self.user_stack_data, self.default_data)

    def set_value(self, current_key, user_values, default_values):
        if current_key in YamlFields.complex_object_field_mapping:
            cofm = YamlFields.complex_object_field_mapping[current_key]
            if cofm.is_list:
                value = []
                if current_key in user_values and isinstance(user_values[current_key], list):
                    for nested_user_values in user_values[current_key]:
                        complex_params = self.get_complex_params(current_key, nested_user_values, cofm.key_list,
                                                                 default_values)
                        value.append(cofm.constructor(**complex_params))
            else:
                nested_user_values = {}
                if current_key in user_values:
                    nested_user_values = user_values[current_key]
                complex_params = self.get_complex_params(current_key, nested_user_values, cofm.key_list, default_values)
                value = cofm.constructor(**complex_params)
        else:
            value = user_values.get(current_key, default_values[current_key])
        return value

    def get_complex_params(self, current_key, nested_user_values, complex_key_list, default_values):
        complex_params = {}
        for complex_key in complex_key_list:
            if complex_key in default_values:
                nested_default_values = default_values
            else:
                nested_default_values = default_values[current_key]
            complex_params[complex_key] = self.set_value(complex_key, nested_user_values, nested_default_values)
        return complex_params

    @staticmethod
    def validate_yaml(data, schema):
        """
        Validates a given data structure against a cerberus schema and raises a validation error if there are any issues
        :param data:  inbound data structure to validate
        :param schema: cerberus schema to validate against
        """
        validator = cerberus.Validator()

        if not validator.validate(data, schema):
            raise cerberus.ValidationError('Errors were found in the supplied Yaml values. See below errors: \n'
                                           '{0}'.format(validator.errors))
