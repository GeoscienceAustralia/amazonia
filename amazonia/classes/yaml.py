#!/usr/bin/python3
"""
Ingest User YAML and defaults YAML
Overwrite defaults YAML with User YAML
"""
import os

import cerberus
from amazonia.classes.util import read_yaml
from amazonia.classes.yaml_fields import YamlFields


class InvalidYamlStructureError(Exception):
    """
    Exception if YAML structure is invalid
    """
    def __init__(self, value):
        self.value = value


class Yaml(object):
    """
    Setting these as class variables rather than instance variables so that they can be resolved and referred to
    statically
    """

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # cerberus schema file location
    cerberus_schema = read_yaml(os.path.join(__location__, '../schemas/cerberus_schema.yaml'))

    def __init__(self, user_stack_data, default_data):
        """
        Initializes united, user and default data dictionaries, these dictionaries form trees of values that are
        ultimately mapped to various Amazonia classes
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()

        # Validate user and default yaml against the provided schema before attempting to combine them.
        self.validate_yaml(self.user_stack_data, self.cerberus_schema)
        self.validate_yaml(self.default_data, self.cerberus_schema)

        # Beginning with the "stack" object, process each field
        for stack_key in YamlFields.stack_key_list:
            self.united_data[stack_key] = self.set_value(stack_key, self.user_stack_data, self.default_data)

    def set_value(self, current_key, user_values, default_values):
        """
        Given a field (current_key), check if it's a simple field (just a value or list) or a complex field (dictionary
        or list of dictionaries).
        :param current_key: The current field to process
        :param user_values: user supplied yaml dictionary
        :param default_values: supplied defaults to interpose with user fields
        :return: The value, either a simple field or complex object(s)
        """
        # check if the current field corresponds is a complex object
        if current_key in YamlFields.complex_object_field_mapping:
            cofm = YamlFields.complex_object_field_mapping[current_key]
            # if the current field is a list of complex objects
            if cofm.is_list:
                # initialise empty list to store field values in
                value = []
                # if the current field is set in user input and that it is a valid list
                # Note: this assumes that a field of this type that has not been specified by the user will become an
                # empty list
                if current_key in user_values and isinstance(user_values[current_key], list):
                    # subset of user values and build a parameter dictionary to initialise complex object constructor
                    for nested_user_values in user_values[current_key]:
                        complex_params = self.get_complex_params(current_key, nested_user_values, cofm.key_list,
                                                                 default_values)
                        # initialise complex object with parameter dictionary and append to list of values for this
                        # field
                        value.append(cofm.constructor(**complex_params))
            else:
                # initialise an empty dictionary to process against default values
                nested_user_values = {}
                # replace empty dictionary with user values if specified
                if current_key in user_values:
                    nested_user_values = user_values[current_key]
                # Note: in contrast to the above, Amazonia will initialise a single complex object with defaults rather
                # than an undefined object
                complex_params = self.get_complex_params(current_key, nested_user_values, cofm.key_list, default_values)
                # initialise complex
                value = cofm.constructor(**complex_params)
        # if simple field, return the user value or if not set the corresponding default value
        else:
            value = user_values.get(current_key, default_values[current_key])
        return value

    def get_complex_params(self, current_key, nested_user_values, complex_key_list, default_values):
        """
        For a given field of a complex object, determine if default is available in current "level" of default value
        tree or is nested within an object corresponding to the current key, then build a dictionary containing the
        values to initialise the complex object with
        :param current_key: the field name of the complex object
        :param nested_user_values: sub dictionary of user values corresponding to current key
        :param complex_key_list: field name list of complex object
        :param default_values: sub dictionary of default values corresponding to current key
        :return: return dictionary containing complex object parameters
        """
        # initialise a dictionary to hold complex parameters
        complex_params = {}
        # process each field in the complex object
        for complex_key in complex_key_list:
            # is the complex field defined at the current level of the default dictionary
            if complex_key in default_values:
                nested_default_values = default_values
            # or is it nested in a dictionary of the same name
            elif current_key in default_values:
                nested_default_values = default_values[current_key]
            # raise an exception if both the current field name and the complex field name are not available in the
            # defaults dictionary
            else:
                raise InvalidYamlStructureError('Error: could not find fields {0} or {1} in default values {2}'
                                                .format(complex_key, current_key, default_values))
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
