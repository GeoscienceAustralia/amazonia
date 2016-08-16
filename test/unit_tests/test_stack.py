from amazonia.classes.stack import Stack, DuplicateUnitNameError
from nose.tools import *
from troposphere import Tags, Ref

userdata = keypair = instance_type = code_deploy_service_role = vpc_cidr = public_cidr = \
    minsize = maxsize = path2ping = nat_image_id = jump_image_id = unit_image_id = health_check_grace_period = \
    health_check_type = db_instance_type = db_engine = db_port = db_hdd_size = owner_emails = nat_alerting = \
    db_backup_window = db_backup_retention = db_maintenance_window = db_storage_type = block_devices_config = None
availability_zones = []
home_cidrs = []
instanceports = []
loadbalancerports = []
protocols = []


def setup_resources():
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instanceports, loadbalancerports, protocols, minsize, maxsize, path2ping, home_cidrs, \
        nat_image_id, jump_image_id, health_check_grace_period, health_check_type, unit_image_id, db_instance_type, \
        db_engine, db_port, db_hdd_size, owner_emails, nat_alerting, db_backup_window, db_backup_retention, \
        db_maintenance_window, db_storage_type, block_devices_config
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
    nat_image_id = 'ami-53371f30'
    jump_image_id = 'ami-dc361ebf'
    unit_image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'
    code_deploy_service_role = 'arn:aws:iam::1234567890124 :role/CodeDeployServiceRole'
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
    owner_emails = ['some@email.com']
    nat_alerting = False

    db_instance_type = 'db.m1.small'
    db_engine = 'postgres'
    db_port = '5432'
    db_hdd_size = 5
    db_backup_window = '17:00-17:30'
    db_backup_retention = '4'
    db_maintenance_window = 'Mon:01:00-Mon:01:30'
    db_storage_type = 'gp2'

    block_devices_config = [{
        'device_name': '/dev/xvda',
        'ebs_volume_size': '15',
        'ebs_volume_type': 'gp2',
        'ebs_encrypted': False,
        'ebs_snapshot_id': '',
        'virtual_name': False},{
        'device_name': '/dev/sda2',
        'ebs_volume_size': '',
        'ebs_volume_type': '',
        'ebs_encrypted': False,
        'ebs_snapshot_id': '',
        'virtual_name': True
    }]


@with_setup(setup_resources)
def test_stack():
    """ Test stack structure
    """
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

    assert_equals(len(stack.units), 4)


def test_duplicate_unit_names():
    """ Test 3 different variations of duplicate unit names
    """
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
        'stack_hosted_zone_name': None,
        'iam_instance_profile_arn': None,
        'owner_emails': owner_emails,
        'nat_alerting': nat_alerting,
        'autoscaling_units': [{'unit_title': 'app1',
                               'asg_config': {
                                   'minsize': minsize,
                                   'maxsize': maxsize,
                                   'image_id': unit_image_id,
                                   'instance_type': instance_type,
                                   'health_check_grace_period': health_check_grace_period,
                                   'health_check_type': health_check_type,
                                   'userdata': userdata,
                                   'iam_instance_profile_arn': None,
                                   'sns_topic_arn': None,
                                   'sns_notification_types': None,
                                   'block_devices_config': block_devices_config
                               },
                               'elb_config': {
                                   'protocols': protocols,
                                   'instanceports': instanceports,
                                   'loadbalancerports': loadbalancerports,
                                   'path2ping': path2ping,
                                   'elb_log_bucket': None,
                                   'public_unit': True,
                                   'unit_hosted_zone_name': None
                               },
                               'dependencies': ['app2', 'db1'],
                               },
                              {'unit_title': 'app1',
                               'elb_config': {
                                   'protocols': protocols,
                                   'instanceports': instanceports,
                                   'loadbalancerports': loadbalancerports,
                                   'path2ping': path2ping,
                                   'elb_log_bucket': None,
                                   'public_unit': True,
                                   'unit_hosted_zone_name': None
                               },
                               'asg_config': {
                                   'minsize': minsize,
                                   'maxsize': maxsize,
                                   'image_id': unit_image_id,
                                   'instance_type': instance_type,
                                   'health_check_grace_period': health_check_grace_period,
                                   'health_check_type': health_check_type,
                                   'userdata': userdata,
                                   'iam_instance_profile_arn': None,
                                   'sns_topic_arn': None,
                                   'sns_notification_types': None,
                                   'hdd_size': None
                               },
                               'dependencies': [],
                               }],
        'database_units': [],
        'zd_autoscaling_units': []
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
        'zd_autoscaling_units': [],
        'stack_hosted_zone_name': None,
        'iam_instance_profile_arn': None,
        'owner_emails': owner_emails,
        'nat_alerting': nat_alerting,
        'database_units': [{'unit_title': 'db1',
                            'database_config': {
                                'db_instance_type': db_instance_type,
                                'db_engine': db_engine,
                                'db_port': db_port,
                                'db_hdd_size': db_hdd_size,
                                'db_snapshot_id': None,
                                'db_name': 'MyDb1',
                                'db_backup_window': db_backup_window,
                                'db_backup_retention': db_backup_retention,
                                'db_maintenance_window': db_maintenance_window,
                                'db_storage_type': db_storage_type
                            }
                            },
                           {'unit_title': 'db1',
                            'database_config': {
                                'db_instance_type': db_instance_type,
                                'db_engine': db_engine,
                                'db_port': db_port,
                                'db_hdd_size': db_hdd_size,
                                'db_snapshot_id': None,
                                'db_name': 'MyDb2',
                                'db_backup_window': db_backup_window,
                                'db_backup_retention': db_backup_retention,
                                'db_maintenance_window': db_maintenance_window,
                                'db_storage_type': db_storage_type
                            }
                            }]
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
        'stack_hosted_zone_name': None,
        'iam_instance_profile_arn': None,
        'owner_emails': owner_emails,
        'nat_alerting': nat_alerting,
        'zd_autoscaling_units': [],
        'autoscaling_units': [{'unit_title': 'app1',
                               'elb_config': {
                                   'protocols': protocols,
                                   'instanceports': instanceports,
                                   'loadbalancerports': loadbalancerports,
                                   'path2ping': path2ping,
                                   'unit_hosted_zone_name': None,
                                   'elb_log_bucket': None,
                                   'public_unit': True,
                               },
                               'asg_config': {
                                   'minsize': minsize,
                                   'maxsize': maxsize,
                                   'image_id': unit_image_id,
                                   'instance_type': instance_type,
                                   'health_check_grace_period': health_check_grace_period,
                                   'health_check_type': health_check_type,
                                   'userdata': userdata,
                                   'iam_instance_profile_arn': None,
                                   'sns_topic_arn': None,
                                   'sns_notification_types': None,
                                   'block_devices_config': block_devices_config
                               },
                               'dependencies': ['app2', 'db1'],
                               }],
        'database_units': [{'unit_title': 'app1',
                            'database_config': {
                                'db_instance_type': db_instance_type,
                                'db_engine': db_engine,
                                'db_port': db_port,
                                'db_hdd_size': db_hdd_size,
                                'db_snapshot_id': None,
                                'db_name': 'MyDb',
                                'db_backup_window': db_backup_window,
                                'db_backup_retention': db_backup_retention,
                                'db_maintenance_window': db_maintenance_window,
                                'db_storage_type': db_storage_type
                            }
                            }]
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
        'stack_hosted_zone_name': None,
        'iam_instance_profile_arn': None,
        'owner_emails': owner_emails,
        'nat_alerting': nat_alerting,
        'zd_autoscaling_units': [{'unit_title': 'zdapp1',
                                  'elb_config': {
                                      'protocols': protocols,
                                      'instanceports': instanceports,
                                      'loadbalancerports': loadbalancerports,
                                      'path2ping': path2ping,
                                      'unit_hosted_zone_name': None,
                                      'elb_log_bucket': None,
                                      'public_unit': True,
                                  },
                                  'blue_asg_config': {
                                      'minsize': minsize,
                                      'maxsize': maxsize,
                                      'image_id': unit_image_id,
                                      'instance_type': instance_type,
                                      'health_check_grace_period': health_check_grace_period,
                                      'health_check_type': health_check_type,
                                      'userdata': userdata,
                                      'iam_instance_profile_arn': None,
                                      'sns_topic_arn': None,
                                      'sns_notification_types': None,
                                      'block_devices_config': block_devices_config
                                  },
                                  'green_asg_config': {
                                      'minsize': minsize,
                                      'maxsize': maxsize,
                                      'image_id': unit_image_id,
                                      'instance_type': instance_type,
                                      'health_check_grace_period': health_check_grace_period,
                                      'health_check_type': health_check_type,
                                      'userdata': userdata,
                                      'iam_instance_profile_arn': None,
                                      'sns_topic_arn': None,
                                      'sns_notification_types': None,
                                      'block_devices_config': block_devices_config
                                  },
                                  'zd_state': 'blue',
                                  'dependencies': ['app2', 'db1'],
                                  },
                                 {'unit_title': 'zdapp1',
                                  'elb_config': {
                                      'protocols': protocols,
                                      'instanceports': instanceports,
                                      'loadbalancerports': loadbalancerports,
                                      'path2ping': path2ping,
                                      'unit_hosted_zone_name': None,
                                      'elb_log_bucket': None,
                                      'public_unit': True,
                                  },
                                  'blue_asg_config': {
                                      'minsize': minsize,
                                      'maxsize': maxsize,
                                      'image_id': unit_image_id,
                                      'instance_type': instance_type,
                                      'health_check_grace_period': health_check_grace_period,
                                      'health_check_type': health_check_type,
                                      'userdata': userdata,
                                      'iam_instance_profile_arn': None,
                                      'sns_topic_arn': None,
                                      'sns_notification_types': None,
                                      'block_devices_config': block_devices_config
                                  },
                                  'green_asg_config': {
                                      'minsize': minsize,
                                      'maxsize': maxsize,
                                      'image_id': unit_image_id,
                                      'instance_type': instance_type,
                                      'health_check_grace_period': health_check_grace_period,
                                      'health_check_type': health_check_type,
                                      'userdata': userdata,
                                      'iam_instance_profile_arn': None,
                                      'sns_topic_arn': None,
                                      'sns_notification_types': None,
                                      'block_devices_config': block_devices_config
                                  },
                                  'zd_state': 'blue',
                                  'dependencies': ['app2', 'db1'],
                                  }
                                 ],
        'autoscaling_units': [],
        'database_units': []
    })


def create_stack(stack_title):
    """
    Helper function to create a stack with default values
    :param stack_title: Title of stack
    :return new stack
    """
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instanceports, loadbalancerports, protocols, minsize, maxsize, path2ping, home_cidrs, \
        nat_image_id, jump_image_id, health_check_grace_period, health_check_type, unit_image_id, db_instance_type, \
        db_engine, db_port, owner_emails, nat_alerting, db_backup_window, db_backup_retention, db_maintenance_window, \
        db_storage_type, block_devices_config

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
        stack_hosted_zone_name=None,
        iam_instance_profile_arn=None,
        owner_emails=owner_emails,
        nat_alerting=nat_alerting,
        zd_autoscaling_units=[{'unit_title': 'zdapp1',
                               'elb_config': {
                                   'protocols': protocols,
                                   'instanceports': instanceports,
                                   'loadbalancerports': loadbalancerports,
                                   'path2ping': path2ping,
                                   'unit_hosted_zone_name': None,
                                   'elb_log_bucket': None,
                                   'public_unit': True,
                               },
                               'blue_asg_config': {
                                   'minsize': minsize,
                                   'maxsize': maxsize,
                                   'image_id': unit_image_id,
                                   'instance_type': instance_type,
                                   'health_check_grace_period': health_check_grace_period,
                                   'health_check_type': health_check_type,
                                   'userdata': userdata,
                                   'iam_instance_profile_arn': None,
                                   'sns_topic_arn': None,
                                   'sns_notification_types': None,
                                   'block_devices_config': block_devices_config
                               },
                               'green_asg_config': {
                                   'minsize': minsize,
                                   'maxsize': maxsize,
                                   'image_id': unit_image_id,
                                   'instance_type': instance_type,
                                   'health_check_grace_period': health_check_grace_period,
                                   'health_check_type': health_check_type,
                                   'userdata': userdata,
                                   'iam_instance_profile_arn': None,
                                   'sns_topic_arn': None,
                                   'sns_notification_types': None,
                                   'block_devices_config': block_devices_config
                               },
                               'zd_state': 'blue',
                               'dependencies': ['app2', 'db1'],
                               }],
        autoscaling_units=[{'unit_title': 'app1',
                            'elb_config': {
                                'protocols': protocols,
                                'instanceports': instanceports,
                                'loadbalancerports': loadbalancerports,
                                'path2ping': path2ping,
                                'unit_hosted_zone_name': None,
                                'elb_log_bucket': None,
                                'public_unit': True,
                            },
                            'asg_config': {
                                'minsize': minsize,
                                'maxsize': maxsize,
                                'image_id': unit_image_id,
                                'instance_type': instance_type,
                                'health_check_grace_period': health_check_grace_period,
                                'health_check_type': health_check_type,
                                'userdata': userdata,
                                'iam_instance_profile_arn': None,
                                'sns_topic_arn': None,
                                'sns_notification_types': None,
                                'block_devices_config': block_devices_config
                            },
                            'dependencies': ['app2', 'db1'],
                            },
                           {'unit_title': 'app2',
                            'elb_config': {
                                'protocols': protocols,
                                'instanceports': instanceports,
                                'loadbalancerports': loadbalancerports,
                                'path2ping': path2ping,
                                'unit_hosted_zone_name': None,
                                'elb_log_bucket': None,
                                'public_unit': True,
                            },
                            'asg_config': {
                                'minsize': minsize,
                                'maxsize': maxsize,
                                'image_id': unit_image_id,
                                'instance_type': instance_type,
                                'health_check_grace_period': health_check_grace_period,
                                'health_check_type': health_check_type,
                                'userdata': userdata,
                                'iam_instance_profile_arn': None,
                                'sns_topic_arn': None,
                                'sns_notification_types': None,
                                'block_devices_config': block_devices_config
                            },
                            'dependencies': []
                            }],
        database_units=[{'unit_title': 'db1',
                         'database_config': {
                             'db_instance_type': db_instance_type,
                             'db_engine': db_engine,
                             'db_port': db_port,
                             'db_hdd_size': db_hdd_size,
                             'db_snapshot_id': None,
                             'db_name': 'MyDb',
                             'db_backup_window': db_backup_window,
                             'db_backup_retention': db_backup_retention,
                             'db_maintenance_window': db_maintenance_window,
                             'db_storage_type': db_storage_type
                         }
                         }
                        ]
    )
    return stack
