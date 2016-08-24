#!/usr/bin/python3
"""
Ingest User YAML and defaults YAML
Overwrite defaults YAML with User YAML
"""
import os
import re
import cerberus
from amazonia.classes.util import read_yaml


class Yaml(object):
    """
    Setting these as class variables rather than instance variables so that they can be resolved and referred to
    statically
    """

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    """ cerberus schema file location """
    cerberus_schema = read_yaml(os.path.join(__location__, '../schemas/cerberus_schema.yaml'))

    """ elb_config field list"""
    elb_config_key_list = ['protocols',
                           'instanceports',
                           'loadbalancerports',
                           'elb_health_check',
                           'public_unit',
                           'elb_log_bucket',
                           'unit_hosted_zone_name',
                           'ssl_certificate_id'
                           ]

    """asg_config field list"""
    asg_config_key_list = ['sns_topic_arn',
                           'sns_notification_types',
                           'health_check_grace_period',
                           'health_check_type',
                           'minsize',
                           'maxsize',
                           'image_id',
                           'instance_type',
                           'userdata',
                           'iam_instance_profile_arn',
                           'block_devices_config'
                           ]

    """asg_config field list"""
    block_devices_config_key_list = ['device_name',
                                     'ebs_volume_size',
                                     'ebs_volume_type',
                                     'ebs_encrypted',
                                     'ebs_snapshot_id',
                                     'virtual_name',
                                     ]

    """database_config field list"""
    database_config_key_list = ['db_name',
                                'db_instance_type',
                                'db_engine',
                                'db_port',
                                'db_hdd_size',
                                'db_snapshot_id',
                                'db_backup_window',
                                'db_backup_retention',
                                'db_maintenance_window',
                                'db_storage_type']

    """stack parameter field list"""
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
                      'stack_hosted_zone_name',
                      'zd_autoscaling_units',
                      'autoscaling_units',
                      'database_units',
                      'iam_instance_profile_arn',
                      'owner_emails',
                      'nat_alerting']

    """unit structure and field list"""
    unit_key_list = {'zd_autoscaling_units': ['unit_title',
                                              'dependencies',
                                              'elb_config',
                                              'blue_asg_config',
                                              'green_asg_config'
                                              ],
                     'autoscaling_units': ['unit_title',
                                           'dependencies',
                                           'elb_config',
                                           'asg_config'
                                           ],
                     'database_units': ['unit_title',
                                        'database_config'
                                        ]
                     }

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

        self.set_values()
        # Validate the combined yaml against the provided schema
        self.validate_yaml(self.united_data, self.cerberus_schema)

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
                if unit_value == 'database_config':
                    user_database_config = self.user_stack_data[unit_type][unit].get(unit_value, {})
                    user_database_config = {} if user_database_config is None else user_database_config
                    self.united_data[unit_type][unit][unit_value] = self.set_nested_object_values(
                        user_database_config, self.default_data['database_config'],
                        self.database_config_key_list)
                elif unit_value == 'elb_config':
                    user_elb_config = self.user_stack_data[unit_type][unit].get(unit_value, {})
                    user_elb_config = {} if user_elb_config is None else user_elb_config
                    self.united_data[unit_type][unit][unit_value] = self.set_nested_object_values(
                        user_elb_config, self.default_data['elb_config'],
                        self.elb_config_key_list)
                elif unit_value in ['asg_config', 'common_asg_config', 'blue_asg_config', 'green_asg_config']:
                    user_asg_config = self.user_stack_data[unit_type][unit].get(unit_value, {})
                    user_asg_config = {} if user_asg_config is None else user_asg_config
                    self.united_data[unit_type][unit][unit_value] = self.set_nested_object_values(
                        user_asg_config, self.default_data['asg_config'],
                        self.asg_config_key_list)
                else:
                    self.united_data[unit_type][unit][unit_value] = \
                        self.user_stack_data[unit_type][unit].get(unit_value, self.default_data[unit_value])

    def set_nested_object_values(self, nested_object_user_data, nested_object_default, nested_object_type):
        """
        Set fields for a nested object (asg_config, elb_config, database_config etc)
        :param nested_object_user_data: user nested object
        :param nested_object_default:  nested object default values
        :param nested_object_type: nested object type (asg_config, elb_config, database_config etc)
        :return: unified nested object
        """
        unified_object = {}
        minsize = 0
        maxsize = 0
        for object_key in nested_object_type:
            if object_key == 'unit_hosted_zone_name':
                unified_object[object_key] = nested_object_user_data.get(object_key,
                                                                         self.united_data['stack_hosted_zone_name'])
            else:
                unified_object[object_key] = nested_object_user_data.get(object_key, nested_object_default[object_key])

            # Validate for unecrypted aws access ids and aws secret keys
            if object_key == 'userdata' and unified_object['userdata'] is not None:
                self.detect_unencrypted_access_keys(unified_object['userdata'])
            # Validate that minsize is less than maxsize
            if object_key == 'minsize':
                minsize = unified_object[object_key]
                maxsize = nested_object_user_data.get('maxsize', nested_object_default['maxsize'])
            if minsize > maxsize:
                raise cerberus.ValidationError('Autoscaling unit minsize ({0}) cannot be '
                                               'larger than maxsize ({1})'.format(minsize, maxsize))
        return unified_object

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
