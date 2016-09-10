from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.cf_cache_behavior_config import CFCacheBehavior
from amazonia.classes.cf_distribution_config import CFDistributionConfig
from amazonia.classes.cf_origins_config import CFOriginsConfig
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.stack import Stack, DuplicateUnitNameError
from amazonia.classes.util import get_cf_friendly_name
from nose.tools import *
from troposphere import Tags, Ref

userdata = keypair = instance_type = code_deploy_service_role = vpc_cidr = public_cidr = \
    minsize = maxsize = elb_health_check = nat_image_id = jump_image_id = unit_image_id = health_check_grace_period = \
    health_check_type = db_instance_type = db_engine = db_port = db_hdd_size = owner_emails = nat_alerting = \
    db_backup_window = db_backup_retention = db_maintenance_window = db_storage_type = block_devices_config = None
availability_zones = []
home_cidrs = []
instance_port = []
loadbalancer_port = []
instance_protocol = []
loadbalancer_protocol = []


def setup_resources():
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instance_port, loadbalancer_port, instance_protocol, loadbalancer_protocol, minsize, maxsize, \
        elb_health_check, home_cidrs, nat_image_id, jump_image_id, health_check_grace_period, health_check_type, \
        unit_image_id, db_instance_type, db_engine, db_port, db_hdd_size, owner_emails, nat_alerting, \
        db_backup_window, db_backup_retention, db_maintenance_window, db_storage_type, block_devices_config, \
        healthy_threshold, unhealthy_threshold, interval, timeout
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
    instance_port = ['80']
    loadbalancer_port = ['80']
    instance_protocol = ['HTTP']
    loadbalancer_protocol = ['HTTP']
    minsize = 1
    maxsize = 1
    elb_health_check = 'HTTP:80/index.html'
    healthy_threshold = 10
    unhealthy_threshold = 2
    interval = 300
    timeout = 30
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

    block_devices_config = [BlockDevicesConfig(
        device_name='/dev/xvda',
        ebs_volume_size='15',
        ebs_volume_type='gp2',
        ebs_encrypted=False,
        ebs_snapshot_id=None,
        virtual_name=False), BlockDevicesConfig(
        device_name='/dev/sda2',
        ebs_volume_size='',
        ebs_volume_type='',
        ebs_encrypted=False,
        ebs_snapshot_id='',
        virtual_name=True
    )]


@with_setup(setup_resources)
def test_stack():
    """ Test stack structure
    """
    stack = create_stack()
    assert_equals(stack.code_deploy_service_role, code_deploy_service_role)
    assert_equals(stack.keypair, keypair)
    assert_equals(stack.availability_zones, availability_zones)
    assert_equals(stack.vpc_cidr, vpc_cidr)
    [assert_equals(stack.home_cidrs[num], home_cidrs[num]) for num in range(len(home_cidrs))]
    assert_equals(stack.public_cidr, {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})

    assert_equals(stack.vpc.title, 'Vpc')
    assert_equals(stack.vpc.CidrBlock, vpc_cidr)
    assert_is(type(stack.vpc.Tags), Tags)

    assert_equals(stack.internet_gateway.title, 'Ig')
    assert_is(type(stack.internet_gateway.Tags), Tags)

    assert_equals(stack.gateway_attachment.title, 'IgAtch')
    assert_is(type(stack.gateway_attachment.VpcId), Ref)
    assert_is(type(stack.gateway_attachment.InternetGatewayId), Ref)

    assert_equals(stack.public_route_table.title, 'PubRouteTable')
    assert_is(type(stack.public_route_table.VpcId), Ref)
    assert_is(type(stack.public_route_table.Tags), Tags)

    for az in availability_zones:
        assert_equals(stack.private_route_tables[az].title, get_cf_friendly_name(az) + 'PriRouteTable')
        assert_is(type(stack.private_route_tables[az].VpcId), Ref)
        assert_is(type(stack.private_route_tables[az].Tags), Tags)

    assert_equals(stack.nat.single.SourceDestCheck, 'false')
    assert_equals(stack.jump.single.SourceDestCheck, 'true')

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = stack.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = stack.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))

    assert_equals(len(stack.units), 7)


def test_highly_available_nat_stack():
    """ Test for nat gateway configuration"""
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instance_port, loadbalancer_port, instance_protocol, loadbalancer_protocol, minsize, maxsize, \
        elb_health_check, home_cidrs, nat_image_id, jump_image_id, health_check_grace_period, health_check_type, \
        unit_image_id, db_instance_type, db_engine, db_port, owner_emails, nat_alerting, db_backup_window, \
        db_backup_retention, db_maintenance_window, db_storage_type, block_devices_config, healthy_threshold, \
        unhealthy_threshold, interval, timeout

    stack = Stack(
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
        public_hosted_zone_name=None,
        private_hosted_zone_name='private.lan.',
        iam_instance_profile_arn=None,
        owner_emails=owner_emails,
        nat_alerting=nat_alerting,
        nat_highly_available=True,
        zd_autoscaling_units=[],
        autoscaling_units=[],
        database_units=[],
        cf_distribution_units=[],
        api_gateway_units=[],
        lambda_units=[]
    )

    assert_equals(stack.code_deploy_service_role, code_deploy_service_role)
    assert_equals(stack.keypair, keypair)
    assert_equals(stack.availability_zones, availability_zones)
    assert_equals(stack.vpc_cidr, vpc_cidr)
    [assert_equals(stack.home_cidrs[num], home_cidrs[num]) for num in range(len(home_cidrs))]
    assert_equals(stack.public_cidr, {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})

    assert_equals(stack.vpc.title, 'Vpc')
    assert_equals(stack.vpc.CidrBlock, vpc_cidr)
    assert_is(type(stack.vpc.Tags), Tags)

    assert_equals(stack.internet_gateway.title, 'Ig')
    assert_is(type(stack.internet_gateway.Tags), Tags)

    assert_equals(stack.gateway_attachment.title, 'IgAtch')
    assert_is(type(stack.gateway_attachment.VpcId), Ref)
    assert_is(type(stack.gateway_attachment.InternetGatewayId), Ref)

    assert_equals(stack.public_route_table.title, 'PubRouteTable')
    assert_is(type(stack.public_route_table.VpcId), Ref)
    assert_is(type(stack.public_route_table.Tags), Tags)

    for az in availability_zones:
        assert_equals(stack.private_route_tables[az].title, get_cf_friendly_name(az) + 'PriRouteTable')
        assert_is(type(stack.private_route_tables[az].VpcId), Ref)
        assert_is(type(stack.private_route_tables[az].Tags), Tags)

    assert_equals(len(stack.nat_gateways), len(availability_zones))
    assert_equals(stack.jump.single.SourceDestCheck, 'true')

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = stack.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = stack.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))

    assert_equals(len(stack.units), 0)


def test_duplicate_unit_names():
    """ Test for duplicate unit names
    """

    assert_raises(DuplicateUnitNameError, Stack, **{
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
        'public_hosted_zone_name': None,
        'private_hosted_zone_name': 'private.lan.',
        'iam_instance_profile_arn': None,
        'owner_emails': owner_emails,
        'nat_alerting': nat_alerting,
        'nat_highly_available': False,
        'autoscaling_units': [{'unit_title': 'app1',
                               'asg_config': AsgConfig(
                                   minsize=minsize,
                                   maxsize=maxsize,
                                   image_id=unit_image_id,
                                   instance_type=instance_type,
                                   health_check_grace_period=health_check_grace_period,
                                   health_check_type=health_check_type,
                                   userdata=userdata,
                                   iam_instance_profile_arn=None,
                                   sns_topic_arn=None,
                                   sns_notification_types=None,
                                   block_devices_config=block_devices_config,
                                   simple_scaling_policy_config=None
                               ),
                               'elb_config': ElbConfig(
                                   loadbalancer_protocol=loadbalancer_protocol,
                                   instance_protocol=instance_protocol,
                                   instance_port=instance_port,
                                   loadbalancer_port=loadbalancer_port,
                                   elb_health_check=elb_health_check,
                                   elb_log_bucket=None,
                                   public_unit=True,
                                   ssl_certificate_id=None,
                                   healthy_threshold=healthy_threshold,
                                   unhealthy_threshold=unhealthy_threshold,
                                   interval=interval,
                                   timeout=timeout
                               ),
                               'dependencies': [],
                               },
                              {'unit_title': 'app1',
                               'elb_config': ElbConfig(
                                   loadbalancer_protocol=loadbalancer_protocol,
                                   instance_protocol=instance_protocol,
                                   instance_port=instance_port,
                                   loadbalancer_port=loadbalancer_port,
                                   elb_health_check=elb_health_check,
                                   elb_log_bucket=None,
                                   public_unit=True,
                                   ssl_certificate_id=None,
                                   healthy_threshold=healthy_threshold,
                                   unhealthy_threshold=unhealthy_threshold,
                                   interval=interval,
                                   timeout=timeout
                               ),
                               'asg_config': AsgConfig(
                                   minsize=minsize,
                                   maxsize=maxsize,
                                   image_id=unit_image_id,
                                   instance_type=instance_type,
                                   health_check_grace_period=health_check_grace_period,
                                   health_check_type=health_check_type,
                                   userdata=userdata,
                                   iam_instance_profile_arn=None,
                                   sns_topic_arn=None,
                                   sns_notification_types=None,
                                   block_devices_config=None,
                                   simple_scaling_policy_config=None
                               ),
                               'dependencies': [],
                               }],
        'database_units': [],
        'zd_autoscaling_units': [],
        'cf_distribution_units': [],
        'api_gateway_units': [],
        'lambda_units': []
    })


def create_stack():
    """
    Helper function to create a stack with default values
    :return new stack
    """
    global userdata, availability_zones, keypair, instance_type, code_deploy_service_role, vpc_cidr, \
        public_cidr, instance_port, loadbalancer_port, instance_protocol, loadbalancer_protocol, minsize, maxsize, \
        elb_health_check, home_cidrs, nat_image_id, jump_image_id, health_check_grace_period, health_check_type, \
        unit_image_id, db_instance_type, db_engine, db_port, owner_emails, nat_alerting, db_backup_window, \
        db_backup_retention, db_maintenance_window, db_storage_type, block_devices_config, healthy_threshold, \
        unhealthy_threshold, interval, timeout

    stack = Stack(
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
        public_hosted_zone_name=None,
        private_hosted_zone_name='priavte.lan.',
        iam_instance_profile_arn=None,
        owner_emails=owner_emails,
        nat_alerting=nat_alerting,
        nat_highly_available=False,
        zd_autoscaling_units=[{'unit_title': 'zdapp1',
                               'elb_config': ElbConfig(
                                   loadbalancer_protocol=loadbalancer_protocol,
                                   instance_protocol=instance_protocol,
                                   instance_port=instance_port,
                                   loadbalancer_port=loadbalancer_port,
                                   elb_health_check=elb_health_check,
                                   elb_log_bucket=None,
                                   public_unit=True,
                                   ssl_certificate_id=None,
                                   healthy_threshold=healthy_threshold,
                                   unhealthy_threshold=unhealthy_threshold,
                                   interval=interval,
                                   timeout=timeout
                               ),
                               'blue_asg_config': AsgConfig(
                                   minsize=minsize,
                                   maxsize=maxsize,
                                   image_id=unit_image_id,
                                   instance_type=instance_type,
                                   health_check_grace_period=health_check_grace_period,
                                   health_check_type=health_check_type,
                                   userdata=userdata,
                                   iam_instance_profile_arn=None,
                                   sns_topic_arn=None,
                                   sns_notification_types=None,
                                   block_devices_config=block_devices_config,
                                   simple_scaling_policy_config=None
                               ),
                               'green_asg_config': AsgConfig(
                                   minsize=minsize,
                                   maxsize=maxsize,
                                   image_id=unit_image_id,
                                   instance_type=instance_type,
                                   health_check_grace_period=health_check_grace_period,
                                   health_check_type=health_check_type,
                                   userdata=userdata,
                                   iam_instance_profile_arn=None,
                                   sns_topic_arn=None,
                                   sns_notification_types=None,
                                   block_devices_config=block_devices_config,
                                   simple_scaling_policy_config=None
                               ),
                               'dependencies': ['app2', 'db1'],
                               }],
        autoscaling_units=[{'unit_title': 'app1',
                            'elb_config': ElbConfig(
                                loadbalancer_protocol=loadbalancer_protocol,
                                instance_protocol=instance_protocol,
                                instance_port=instance_port,
                                loadbalancer_port=loadbalancer_port,
                                elb_health_check=elb_health_check,
                                elb_log_bucket=None,
                                public_unit=True,
                                ssl_certificate_id=None,
                                healthy_threshold=healthy_threshold,
                                unhealthy_threshold=unhealthy_threshold,
                                interval=interval,
                                timeout=timeout
                            ),
                            'asg_config': AsgConfig(
                                minsize=minsize,
                                maxsize=maxsize,
                                image_id=unit_image_id,
                                instance_type=instance_type,
                                health_check_grace_period=health_check_grace_period,
                                health_check_type=health_check_type,
                                userdata=userdata,
                                iam_instance_profile_arn=None,
                                sns_topic_arn=None,
                                sns_notification_types=None,
                                block_devices_config=block_devices_config,
                                simple_scaling_policy_config=None
                            ),
                            'dependencies': ['app2', 'db1'],
                            },
                           {'unit_title': 'app2',
                            'elb_config': ElbConfig(
                                loadbalancer_protocol=loadbalancer_protocol,
                                instance_protocol=instance_protocol,
                                instance_port=instance_port,
                                loadbalancer_port=loadbalancer_port,
                                elb_health_check=elb_health_check,
                                elb_log_bucket=None,
                                public_unit=True,
                                ssl_certificate_id=None,
                                healthy_threshold=healthy_threshold,
                                unhealthy_threshold=unhealthy_threshold,
                                interval=interval,
                                timeout=timeout
                            ),
                            'asg_config': AsgConfig(
                                minsize=minsize,
                                maxsize=maxsize,
                                image_id=unit_image_id,
                                instance_type=instance_type,
                                health_check_grace_period=health_check_grace_period,
                                health_check_type=health_check_type,
                                userdata=userdata,
                                iam_instance_profile_arn=None,
                                sns_topic_arn=None,
                                sns_notification_types=None,
                                block_devices_config=block_devices_config,
                                simple_scaling_policy_config=None
                            ),
                            'dependencies': []
                            }],
        database_units=[{'unit_title': 'db1',
                         'database_config': DatabaseConfig(
                             db_instance_type=db_instance_type,
                             db_engine=db_engine,
                             db_port=db_port,
                             db_hdd_size=db_hdd_size,
                             db_snapshot_id=None,
                             db_name='MyDb',
                             db_backup_window=db_backup_window,
                             db_backup_retention=db_backup_retention,
                             db_maintenance_window=db_maintenance_window,
                             db_storage_type=db_storage_type
                         )
                         }
                        ],
        cf_distribution_units=[{'unit_title': 'cfdist1',
                                'cf_origins_config': [CFOriginsConfig(
                                    domain_name='amazonia-elb-bucket.s3.amazonaws.com',
                                    origin_id='S3-amazonia-elb-bucket',
                                    origin_path='',
                                    custom_headers={
                                        'Origin':'http://www.domain.com',
                                        'Accept':'True'
                                    },
                                    origin_policy={
                                        'is_s3': True,
                                        'origin_access_identity': 'originaccessid1'
                                    }
                                ),
                                    CFOriginsConfig(
                                        domain_name=
                                        'amazonia-myStackap-LXYP1MFWT9UC-145363293.ap-southeast-2.elb.amazonaws.com',
                                        origin_id='ELB-amazonia-myStackap-LXYP1MFWT9UC-145363293',
                                        origin_path='/path',
                                        custom_headers={},
                                        origin_policy={
                                            'is_s3': False,
                                            'origin_protocol_policy': 'https-only',
                                            'http_port': 80,
                                            'https_port': 443,
                                            'origin_ssl_protocols': ['TLSv1', 'TLSv1.1', 'TLSv1.2'],
                                        }
                                    )
                                ],
                                'cf_distribution_config': CFDistributionConfig(
                                    aliases=['www.test-stack.gadevs.ga', 'test-stack.gadevs.ga'],
                                    comment='SysTestCFDistribution',
                                    default_root_object='index.html',
                                    enabled=True,
                                    price_class='PriceClass_All',
                                    error_page_path='index.html',
                                    acm_cert_arn='arn.acm.certificate',
                                    minimum_protocol_version='TLSv1',
                                    ssl_support_method='sni-only'
                                ),
                                'cf_cache_behavior_config': [CFCacheBehavior(
                                    is_default=True,
                                    path_pattern='/index.html',
                                    allowed_methods=['GET', 'HEAD'],
                                    cached_methods=['GET', 'HEAD'],
                                    target_origin_id='S3-bucket-id',
                                    forward_cookies='all',
                                    forwarded_headers=['Accept', 'Set-Cookie'],
                                    viewer_protocol_policy='allow-all',
                                    min_ttl=0,
                                    default_ttl=0,
                                    max_ttl=0,
                                    trusted_signers=['self'],
                                    query_string='False'
                                ),
                                    CFCacheBehavior(
                                        is_default=False,
                                        path_pattern='/login.js',
                                        allowed_methods=['GET', 'POST', 'HEAD', 'DELETE', 'OPTIONS', 'PATCH', 'PUT'],
                                        cached_methods=['GET', 'HEAD'],
                                        target_origin_id='www-origin',
                                        forward_cookies='all',
                                        forwarded_headers=['Accept', 'Set-Cookie'],
                                        viewer_protocol_policy='https-only',
                                        min_ttl=0,
                                        default_ttl=0,
                                        max_ttl=0,
                                        trusted_signers=['self'],
                                        query_string='True'
                                    )
                                ]
                                }],
        api_gateway_units=[{'unit_title': 'test',
                            'method_config': [
                                ApiGatewayMethodConfig(
                                    method_name='login',
                                    lambda_unit='lambda1',
                                    httpmethod='POST',
                                    authorizationtype='NONE',
                                    request_config=ApiGatewayRequestConfig(
                                        templates={'application/json': ''},
                                        parameters={'somemapping': 'somefield'}
                                    ),
                                    response_config=[ApiGatewayResponseConfig(
                                        templates={'application/json': ''},
                                        parameters={'somemapping': 'somefield'},
                                        statuscode='200',
                                        models={'application/json': 'Empty'},
                                        selectionpattern=''
                                    )]
                                )
                            ],
                            'deployment_config': []
                            }],
        lambda_units=[{'unit_title': 'lambda1',
                       'dependencies': ['db1'],
                       'lambda_config': LambdaConfig(
                           lambda_s3_bucket='bucket_name',
                           lambda_s3_key='key_name',
                           lambda_description='blah',
                           lambda_function_name='my_function',
                           lambda_handler='main',
                           lambda_memory_size=128,
                           lambda_role_arn='test_arn',
                           lambda_runtime='python2.7',
                           lambda_timeout=1,
                           lambda_schedule='cron(0/5 * * * ? *)'
                       )
                       }
                      ]
    )
    return stack
