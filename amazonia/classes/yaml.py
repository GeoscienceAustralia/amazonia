#!/usr/bin/python3
"""
Ingest User YAML and defaults YAML
Overwrite defaults YAML with User YAML
"""
import re
import cerberus


class Yaml(object):
    """
    Setting these as class variables rather than instance variables so that they can be resolved and referred to
    statically
    """
    stack_key_list = ['stack_title',
                      'code_deploy_service_role',
                      'keypair',
                      'availability_zones',
                      'vpc_cidr',
                      'public_cidr',
                      'jump_image_id',
                      'jump_instance_type',
                      'nat_image_id',
                      'nat_instance_type',
                      'home_cidrs',
                      'autoscaling_units',
                      'database_units']
    unit_key_list = {'autoscaling_units': ['unit_title',
                                           'hosted_zone_name',
                                           'userdata',
                                           'image_id',
                                           'instance_type',
                                           'path2ping',
                                           'protocols',
                                           'loadbalancerports',
                                           'instanceports',
                                           'minsize',
                                           'maxsize',
                                           'health_check_grace_period',
                                           'iam_instance_profile_arn',
                                           'sns_topic_arn',
                                           'sns_notification_types',
                                           'elb_log_bucket',
                                           'health_check_type',
                                           'dependencies'],
                     'database_units': ['unit_title',
                                        'db_instance_type',
                                        'db_engine',
                                        'db_port']
                     }

    def __init__(self, user_stack_data, default_data, schema):
        """
        Initializes united, user and default data dictionaries
        :param user_stack_data: User yaml document used to read stack values
        :param default_data: Company yaml to read in company default values
        """
        self.user_stack_data = user_stack_data
        self.default_data = default_data
        self.united_data = dict()

        # Validate user and default yaml against the provided schema before attempting to combine them.
        self.validate_yaml(self.user_stack_data, schema)
        self.validate_yaml(self.default_data, schema)

        self.set_values()
        # Validate the combined yaml against the provided schema
        self.validate_yaml(self.united_data, schema)

    def set_values(self):
        """
        Assigning values to the united_data dictionary
        Validating values such as vpc cidr, home cidrs, aws access ids and secret keys and reassigning if required
        """
        for stack_key in Yaml.stack_key_list:
            # Add stack key value pairs to united data
            self.united_data[stack_key] = self.user_stack_data.get(stack_key, self.default_data[stack_key])

        for unit_type in Yaml.unit_key_list:
            if unit_type in self.user_stack_data:
                self.set_unit_values_for_type(unit_type)

    def set_unit_values_for_type(self, unit_type):
        """
        Process unit input values for given unit type, validate specific fields such as title and userdata
        :param unit_type: unit type (autoscaling, database, etc)
        """
        for unit, unit_values in enumerate(self.user_stack_data[unit_type]):
            for unit_value in Yaml.unit_key_list[unit_type]:
                self.united_data[unit_type][unit][unit_value] = \
                    self.user_stack_data[unit_type][unit].get(unit_value, self.default_data[unit_value])
                # Validate for unecrypted aws access ids and aws secret keys
                if unit_value == 'userdata':
                    self.detect_unencrypted_access_keys(self.united_data[unit_type][unit]['userdata'])
                # Validate that minsize is less than maxsize
                if unit_value == 'minsize':
                    minsize = self.united_data[unit_type][unit][unit_value]
                    maxsize = self.user_stack_data[unit_type][unit].get('maxsize', self.default_data['maxsize'])
                    if minsize > maxsize:
                        raise cerberus.ValidationError('Autoscaling unit minsize ({0}) cannot be '\
                                                       'larger than maxsize ({1})'.format(minsize, maxsize))


    @staticmethod
    def validate_yaml(data, schema):

        validator = cerberus.Validator()

        if not validator.validate(data, schema):
            raise cerberus.ValidationError('Errors were found in the supplied Yaml values. See below errors: \n'\
                                           '{0}'.format(validator.errors))

    @staticmethod
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
    def __init__(self, value):
        self.value = value

