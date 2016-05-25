from nose.tools import *
from troposphere import Tags, Ref

from amazonia.classes.stack import Stack, DuplicateUnitNameError

userdata = keypair = instance_type = code_deploy_service_role = vpc_cidr = public_cidr = \
    minsize = maxsize = path2ping = nat_image_id = jump_image_id = unit_image_id = health_check_grace_period = \
    health_check_type = db_instance_type = db_engine = db_port = None
availability_zones = []
home_cidrs = []
instanceports = []
loadbalancerports = []
protocols = []


def setup_resources():
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instanceports, loadbalancerports, protocols, minsize, maxsize, path2ping, home_cidrs, \
        nat_image_id, jump_image_id, health_check_grace_period, health_check_type, unit_image_id, db_instance_type, \
        db_engine, db_port
    userdata = """#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
"""
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    keypair = 'pipeline'
    nat_image_id = 'ami-162c0c75'
    jump_image_id = 'ami-05446966'
    unit_image_id = 'ami-05446966'
    instance_type = 't2.nano'
    code_deploy_service_role = 'arn:aws:iam::658691668407:role/CodeDeployServiceRole'
    vpc_cidr = '10.0.0.0/16'
    home_cidrs = [{'name': 'GA', 'cidr': '123.123.12.34/32'}, {'name': 'home', 'cidr': '192.168.0.1/16'}]
    instanceports = ['80']
    loadbalancerports = ['80']
    protocols = ['HTTP']
    minsize = 1
    maxsize = 1
    path2ping = '/index.html'
    public_cidr = {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}
    health_check_grace_period = 300
    health_check_type = 'ELB'

    db_instance_type = 'db.m1.small'
    db_engine = 'postgres'
    db_port = '5432'


@with_setup(setup_resources())
def test_stack():
    """Test stack structure"""
    title = 'app'
    stack = create_stack(stack_title=title)
    assert_equals(stack.title, title)
    assert_equals(stack.code_deploy_service_role, code_deploy_service_role)
    assert_equals(stack.keypair, keypair)
    assert_equals(stack.availability_zones, availability_zones)
    assert_equals(stack.vpc_cidr, vpc_cidr)
    [assert_equals(stack.home_cidrs[num], home_cidrs[num]) for num in range(len(home_cidrs))]
    assert_equals(stack.public_cidr, {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})

    assert_equals(stack.vpc.title, title + 'Vpc')
    assert_equals(stack.vpc.CidrBlock, vpc_cidr)
    assert_is(type(stack.vpc.Tags), Tags)

    assert_equals(stack.internet_gateway.title, title + 'Ig')
    assert_is(type(stack.internet_gateway.Tags), Tags)

    assert_equals(stack.gateway_attachment.title, title + 'IgAtch')
    assert_is(type(stack.gateway_attachment.VpcId), Ref)
    assert_is(type(stack.gateway_attachment.InternetGatewayId), Ref)

    assert_equals(stack.public_route_table.title, title + 'PubRt')
    assert_is(type(stack.public_route_table.VpcId), Ref)
    assert_is(type(stack.public_route_table.Tags), Tags)

    assert_equals(stack.private_route_table.title, title + 'PriRt')
    assert_is(type(stack.private_route_table.VpcId), Ref)
    assert_is(type(stack.private_route_table.Tags), Tags)

    assert_equals(stack.nat.single.SourceDestCheck, 'false')
    assert_equals(stack.jump.single.SourceDestCheck, 'true')

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = stack.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = stack.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))

    assert_equals(len(stack.units), 3)


def test_duplicate_unit_names():
    """Test 3 different variations of duplicate unit names"""
    assert_raises(DuplicateUnitNameError, Stack, **{
        'stack_title': 'TestStack',
        'code_deploy_service_role': code_deploy_service_role,
        'keypair': keypair,
        'availability_zones': availability_zones,
        'vpc_cidr': vpc_cidr,
        'public_cidr': public_cidr,
        'home_cidrs': home_cidrs,
        'jump_image_id': jump_image_id,
        'jump_instance_type': instance_type,
        'nat_image_id': nat_image_id,
        'nat_instance_type': instance_type,
        'autoscaling_units': [{'unit_title': 'app1',
                               'protocols': protocols,
                               'instanceports': instanceports,
                               'loadbalancerports': loadbalancerports,
                               'path2ping': path2ping,
                               'minsize': minsize,
                               'maxsize': maxsize,
                               'image_id': unit_image_id,
                               'instance_type': instance_type,
                               'health_check_grace_period': health_check_grace_period,
                               'health_check_type': health_check_type,
                               'userdata': userdata,
                               'hosted_zone_name': None,
                               'iam_instance_profile_arn': None,
                               'sns_topic_arn': None,
                               'sns_notification_types': None,
                               'elb_log_bucket': None,
                               'dependencies': ['app2', 'db1']},
                              {'unit_title': 'app1',
                               'protocols': protocols,
                               'instanceports': instanceports,
                               'loadbalancerports': loadbalancerports,
                               'path2ping': path2ping,
                               'minsize': minsize,
                               'maxsize': maxsize,
                               'image_id': unit_image_id,
                               'instance_type': instance_type,
                               'health_check_grace_period': health_check_grace_period,
                               'health_check_type': health_check_type,
                               'userdata': userdata,
                               'hosted_zone_name': None,
                               'iam_instance_profile_arn': None,
                               'sns_topic_arn': None,
                               'sns_notification_types': None,
                               'elb_log_bucket': None,
                               'dependencies': []}],
        'database_units': []
    })

    assert_raises(DuplicateUnitNameError, Stack, **{
        'stack_title': 'TestStack',
        'code_deploy_service_role': code_deploy_service_role,
        'keypair': keypair,
        'availability_zones': availability_zones,
        'vpc_cidr': vpc_cidr,
        'public_cidr': public_cidr,
        'home_cidrs': home_cidrs,
        'jump_image_id': jump_image_id,
        'jump_instance_type': instance_type,
        'nat_image_id': nat_image_id,
        'nat_instance_type': instance_type,
        'autoscaling_units': [],
        'database_units': [{'unit_title': 'db1',
                            'db_instance_type': db_instance_type,
                            'db_engine': db_engine,
                            'db_port': db_port},
                           {'unit_title': 'db1',
                            'db_instance_type': db_instance_type,
                            'db_engine': db_engine,
                            'db_port': db_port}]
    })

    assert_raises(DuplicateUnitNameError, Stack, **{
        'stack_title': 'TestStack',
        'code_deploy_service_role': code_deploy_service_role,
        'keypair': keypair,
        'availability_zones': availability_zones,
        'vpc_cidr': vpc_cidr,
        'public_cidr': public_cidr,
        'home_cidrs': home_cidrs,
        'jump_image_id': jump_image_id,
        'jump_instance_type': instance_type,
        'nat_image_id': nat_image_id,
        'nat_instance_type': instance_type,
        'autoscaling_units': [{'unit_title': 'app1',
                               'protocols': protocols,
                               'instanceports': instanceports,
                               'loadbalancerports': loadbalancerports,
                               'path2ping': path2ping,
                               'minsize': minsize,
                               'maxsize': maxsize,
                               'image_id': unit_image_id,
                               'instance_type': instance_type,
                               'health_check_grace_period': health_check_grace_period,
                               'health_check_type': health_check_type,
                               'userdata': userdata,
                               'hosted_zone_name': None,
                               'iam_instance_profile_arn': None,
                               'sns_topic_arn': None,
                               'sns_notification_types': None,
                               'elb_log_bucket': None,
                               'dependencies': ['app2', 'db1']}],
        'database_units': [{'unit_title': 'app1',
                            'db_instance_type': db_instance_type,
                            'db_engine': db_engine,
                            'db_port': db_port}]
    })


def create_stack(stack_title):
    """Helper function to create a stack with default values
    :param stack_title: Title of stack
    :return new stack"""
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instanceports, loadbalancerports, protocols, minsize, maxsize, path2ping, home_cidrs, \
        nat_image_id, jump_image_id, health_check_grace_period, health_check_type, unit_image_id, db_instance_type, \
        db_engine, db_port
    stack = Stack(
        stack_title=stack_title,
        code_deploy_service_role=code_deploy_service_role,
        keypair=keypair,
        availability_zones=availability_zones,
        vpc_cidr=vpc_cidr,
        public_cidr=public_cidr,
        home_cidrs=home_cidrs,
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        autoscaling_units=[{'unit_title': 'app1',
                            'protocols': protocols,
                            'instanceports': instanceports,
                            'loadbalancerports': loadbalancerports,
                            'path2ping': path2ping,
                            'minsize': minsize,
                            'maxsize': maxsize,
                            'image_id': unit_image_id,
                            'instance_type': instance_type,
                            'health_check_grace_period': health_check_grace_period,
                            'health_check_type': health_check_type,
                            'userdata': userdata,
                            'hosted_zone_name': None,
                            'iam_instance_profile_arn': None,
                            'sns_topic_arn': None,
                            'sns_notification_types': None,
                            'elb_log_bucket': None,
                            'dependencies': ['app2', 'db1']},
                           {'unit_title': 'app2',
                            'protocols': protocols,
                            'instanceports': instanceports,
                            'loadbalancerports': loadbalancerports,
                            'path2ping': path2ping,
                            'minsize': minsize,
                            'maxsize': maxsize,
                            'image_id': unit_image_id,
                            'instance_type': instance_type,
                            'health_check_grace_period': health_check_grace_period,
                            'health_check_type': health_check_type,
                            'userdata': userdata,
                            'hosted_zone_name': None,
                            'iam_instance_profile_arn': None,
                            'sns_topic_arn': None,
                            'sns_notification_types': None,
                            'elb_log_bucket': None,
                            'dependencies': []}],
        database_units=[{'unit_title': 'db1',
                         'db_instance_type': db_instance_type,
                         'db_engine': db_engine,
                         'db_port': db_port}]
    )
    return stack
