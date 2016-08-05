#!/usr/bin/python3

import os

import yaml
from amazonia.classes.yaml import Yaml, InsecureVariableError
from cerberus import ValidationError
from nose.tools import *

default_data = None


def setup_resources():
    """
    Create default data yaml
    """
    global default_data

    default_data = open_yaml_file('../../amazonia/defaults.yaml')


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


@with_setup(setup_resources)
def test_complete_valid_values():
    """
    Validate stack yaml value is a list of dictionaries
    Validate that stack value exists in expected list of stack values
    """
    global default_data
    valid_stack_data = open_yaml_file('test_yaml_complete_valid.yaml')
    amz_yaml = Yaml(valid_stack_data, default_data)

    stack_input = amz_yaml.united_data

    # Assert stack values are of type dict
    assert_equals(type(stack_input), dict)

    # Assert that there are no invalid stack keys
    stack_input_set = set(stack_input)
    expected_stack_set = set(Yaml.stack_key_list)
    assert_equals(len(stack_input_set.difference(expected_stack_set)), 0)

    # Assert that there are no stack keys we missed
    assert_equals(len(expected_stack_set.difference(stack_input_set)), 0)

    # Assert correct values
    assert_equals(stack_input['stack_title'], 'testStack')
    assert_equals(stack_input['code_deploy_service_role'], 'arn:aws:iam::1234567890123:role/CodeDeployServiceRole')
    assert_equals(stack_input['keypair'], 'key')
    assert_list_equal(stack_input['availability_zones'], ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'])
    assert_equals(stack_input['vpc_cidr'], '10.0.0.0/16')
    assert_dict_equal(stack_input['public_cidr'], {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})
    assert_equals(stack_input['jump_image_id'], 'ami-dc361ebf')
    assert_equals(stack_input['jump_instance_type'], 't2.micro')
    assert_equals(stack_input['nat_image_id'], 'ami-53371f30')
    assert_equals(stack_input['nat_instance_type'], 't2.micro')
    assert_equals(stack_input['stack_hosted_zone_name'], 'test.org.')
    assert_equals(type(stack_input['home_cidrs']), list)
    assert_equals(len(stack_input['home_cidrs']), 1)
    assert_equals(type(stack_input['autoscaling_units']), list)
    assert_equals(len(stack_input['autoscaling_units']), 2)
    assert_equals(type(stack_input['database_units']), list)
    assert_equals(len(stack_input['database_units']), 1)

    autoscaling_unit_input = stack_input['autoscaling_units'][0]

    # Assert autoscaling unit values are of type dict
    assert_equals(type(autoscaling_unit_input), dict)

    # Assert that there are no invalid autoscaling unit keys
    autoscaling_unit_input_set = set(autoscaling_unit_input.keys())
    expected_autoscaling_unit_set = set(Yaml.unit_key_list['autoscaling_units'])
    assert_equals(len(autoscaling_unit_input_set.difference(expected_autoscaling_unit_set)), 0)

    # Assert that there are no autoscaling unit keys we missed
    assert_equals(len(expected_autoscaling_unit_set.difference(autoscaling_unit_input_set)), 0)

    assert_equals(autoscaling_unit_input['unit_title'], 'app1')
    assert_equals(autoscaling_unit_input['asg_config']['image_id'], 'ami-dc361ebf')
    assert_equals(autoscaling_unit_input['asg_config']['instance_type'], 't2.micro')
    assert_equals(autoscaling_unit_input['elb_config']['path2ping'], '/index.html')
    assert_list_equal(autoscaling_unit_input['elb_config']['protocols'], ['HTTP'])
    assert_list_equal(autoscaling_unit_input['elb_config']['loadbalancerports'], ['80'])
    assert_list_equal(autoscaling_unit_input['elb_config']['instanceports'], ['80'])
    assert_equals(autoscaling_unit_input['asg_config']['minsize'], '1')
    assert_equals(autoscaling_unit_input['asg_config']['maxsize'], '1')
    assert_equals(autoscaling_unit_input['asg_config']['health_check_grace_period'], '300')
    assert_equals(autoscaling_unit_input['asg_config']['iam_instance_profile_arn'],
                  'arn:aws:iam::1234567890124:role/InstanceProfile')
    assert_equals(autoscaling_unit_input['asg_config']['sns_topic_arn'], 'sns_topic_arn')
    assert_equals(autoscaling_unit_input['asg_config']['sns_notification_types'],
                  ['autoscaling:EC2_INSTANCE_LAUNCH',
                   'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                   'autoscaling:EC2_INSTANCE_TERMINATE',
                   'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'])
    assert_equals(autoscaling_unit_input['elb_config']['elb_log_bucket'], 'elb_log_bucket')
    assert_equals(autoscaling_unit_input['asg_config']['health_check_type'], 'ELB')
    assert_list_equal(autoscaling_unit_input['dependencies'], ['app2', 'db1'])
    assert_equals(autoscaling_unit_input['elb_config']['unit_hosted_zone_name'], 'test.org.')

    # Assert that unit is picking up the stack_hosted_zone_name if unit_hosted_zone_name isn't provided
    assert_equals(stack_input['autoscaling_units'][0]['elb_config']['unit_hosted_zone_name'],
                  stack_input['stack_hosted_zone_name'])

    database_unit_input = stack_input['database_units'][0]

    # Assert database unit values are of type dict
    assert_equals(type(database_unit_input), dict)

    # Assert that there are no invalid database unit keys
    database_unit_input_set = set(database_unit_input)
    expected_database_unit_set = set(Yaml.unit_key_list['database_units'])
    assert_equals(len(database_unit_input_set.difference(expected_database_unit_set)), 0)

    # Assert that there are no database unit keys we missed
    assert_equals(len(expected_database_unit_set.difference(database_unit_input_set)), 0)

    assert_equals(database_unit_input['unit_title'], 'db1')
    assert_equals(database_unit_input['database_config']['db_instance_type'], 'db.m1.small')
    assert_equals(database_unit_input['database_config']['db_engine'], 'postgres')
    assert_equals(database_unit_input['database_config']['db_port'], '5432')
    assert_equals(database_unit_input['database_config']['db_name'], 'myDb')


@with_setup(setup_resources)
def test_validate_cidr_yaml():
    """
    Test the detection of invalid CIDRs
    """
    global default_data

    invalid_vpc_cidr_data = open_yaml_file('test_yaml_invalid_vpc_cidr.yaml')
    invalid_home_cidrs_data = open_yaml_file('test_yaml_invalid_home_cidrs.yaml')
    invalid_home_cidr_title_data = open_yaml_file('test_yaml_invalid_home_cidr_title.yaml')
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_vpc_cidr_data,
                                            'default_data': default_data})
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_home_cidrs_data,
                                            'default_data': default_data})
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_home_cidr_title_data,
                                            'default_data': default_data})


@with_setup(setup_resources)
def test_get_invalid_values_yaml():
    """
    Test the detection of unrecognized or invalid keys within YAML files
    """
    global default_data

    invalid_stack_data = open_yaml_file('test_yaml_invalid_key_stack.yaml')
    invalid_autoscaling_unit_data = open_yaml_file('test_yaml_invalid_key_autoscaling_unit.yaml')
    invalid_database_unit_data = open_yaml_file('test_yaml_invalid_key_database_unit.yaml')
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_stack_data,
                                            'default_data': default_data})
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_autoscaling_unit_data,
                                            'default_data': default_data})
    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_database_unit_data,
                                            'default_data': default_data})


@with_setup(setup_resources)
def test_insecure_variables_yaml():
    """
    Test the detection of insecure variables within YAML files
    """
    global default_data

    insecure_access_id = open_yaml_file('test_yaml_insecure_access_id.yaml')
    insecure_secret_key = open_yaml_file('test_yaml_insecure_secret_key.yaml')
    assert_raises(InsecureVariableError, Yaml, **{'user_stack_data': insecure_access_id,
                                                  'default_data': default_data})
    assert_raises(InsecureVariableError, Yaml, **{'user_stack_data': insecure_secret_key,
                                                  'default_data': default_data})


@with_setup(setup_resources)
def test_invalid_min_max_asg():
    """
    Test the detection of a larger minimum that the provided maximum for an auto scaling unit
    """
    global default_data
    invalid_min_max_stack_data = open_yaml_file('test_yaml_invalid_min_max_asg.yaml')

    assert_raises(ValidationError, Yaml, **{'user_stack_data': invalid_min_max_stack_data,
                                            'default_data': default_data})


def test_detect_unencrypted_access_keys():
    """
    Detect unencrypted AWS access ID and AWS secret key
    """
    assert_raises(InsecureVariableError, Yaml.detect_unencrypted_access_keys,
                  **{'userdata': '9VJrJAil2XtEC/B7g+Y+/Fmerk3iqyDH/UIhKjXk'})

    assert_raises(InsecureVariableError, Yaml.detect_unencrypted_access_keys,
                  **{'userdata': 'AKI3ISW6DFTLGVWEDYMQ'})
