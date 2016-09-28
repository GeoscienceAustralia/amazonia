from amazonia.classes.amz_autoscaling import AutoscalingUnit, AutoscalingLeaf
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
from network_setup import get_network_config
from nose.tools import *
from troposphere import Ref

template = network_config = elb_config = asg_config = tree_name = availability_zones = cd_service_role_arn = \
    public_cidr = public_hosted_zone_name = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, elb_config, asg_config, tree_name, availability_zones, cd_service_role_arn, \
        public_cidr, public_hosted_zone_name
    tree_name = 'testtree'
    network_config, template = get_network_config()
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    cd_service_role_arn = 'arn:aws:iam::123456789:role/CodeDeployServiceRole'
    public_cidr = {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}
    public_hosted_zone_name = 'your.domain.'
    block_devices_config = [BlockDevicesConfig(
        device_name='/dev/xvda',
        ebs_volume_size='15',
        ebs_volume_type='gp2',
        ebs_encrypted=False,
        ebs_snapshot_id='',
        virtual_name=False)]

    asg_config = AsgConfig(
        userdata="""
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """,
        health_check_grace_period=300,
        health_check_type='ELB',
        iam_instance_profile_arn='arn:aws:iam::123456789:instance-profile/iam-instance-profile',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        maxsize=1,
        minsize=1,
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None
    )

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='JSESSION'
        )]

    elb_config = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket=None,
        public_unit=True,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30
    )


@with_setup(setup_resources)
def test_autoscaling_unit():
    """Test autoscaling unit structure"""
    title = 'app'
    unit = create_autoscaling_unit(title=title)
    assert_equals(unit.asg.trop_asg.title, title + 'Asg')
    assert_equals(unit.elb.trop_elb.title, title)
    [assert_is(type(lbn), Ref) for lbn in unit.asg.trop_asg.LoadBalancerNames]
    assert_equals(len(unit.asg.egress), 1)
    assert_equals(len(unit.asg.ingress), 2)
    assert_equals(len(unit.elb.ingress), 1)
    assert_equals(len(unit.elb.egress), 1)


@with_setup(setup_resources)
def test_unit_association():
    """Test autoscaling unit flow"""
    create_autoscaling_unit(title='app2')
    unit = create_autoscaling_unit(title='app1', dependencies=['app2:80'])
    assert_equals(len(unit.asg.egress), 2)
    assert_equals(len(unit.asg.ingress), 2)
    assert_equals(len(unit.elb.ingress), 1)
    assert_equals(len(unit.elb.egress), 1)


@with_setup(setup_resources)
def test_autoscaling_leaf():
    """Test autoscaling leaf structure"""
    title = 'app'
    leaf = create_autoscaling_leaf(title=title)
    assert_equals(leaf.asg.trop_asg.title, title + 'Asg')
    assert_equals(leaf.elb.trop_elb.title, title)
    [assert_is(type(lbn), Ref) for lbn in leaf.asg.trop_asg.LoadBalancerNames]
    assert_equals(len(leaf.asg.egress), 1)
    assert_equals(len(leaf.asg.ingress), 2)
    assert_equals(len(leaf.elb.ingress), 1)
    assert_equals(len(leaf.elb.egress), 1)


@with_setup(setup_resources)
def test_leaf_association():
    """Test autoscaling leaf flow"""
    leaf = create_autoscaling_leaf(title='app1', dependencies=['app2:80'])
    assert_equals(len(leaf.asg.egress), 2)
    assert_equals(len(leaf.asg.ingress), 2)
    assert_equals(len(leaf.elb.ingress), 1)
    assert_equals(len(leaf.elb.egress), 1)


def create_autoscaling_leaf(title, dependencies=None):
    """Helper function to create leaf
    :param title: title of leaf
    :param dependencies: optional list of dependencies
    :return new autoscaling leaf
    """
    global template, asg_config, elb_config, tree_name
    return AutoscalingLeaf(tree_name=tree_name, leaf_title=title, asg_config=asg_config, elb_config=elb_config,
                           availability_zones=availability_zones, cd_service_role_arn=cd_service_role_arn,
                           keypair='INSERT_YOUR_KEYPAIR_HERE', template=template, public_cidr=public_cidr,
                           dependencies=dependencies, public_hosted_zone_name=public_hosted_zone_name)


def create_autoscaling_unit(title, dependencies=None):
    """Helper function to create unit
    :param title: title of unit
    :param dependencies: optional list of dependencies
    :return new autoscaling unit
    """
    global template, network_config, asg_config, elb_config
    return AutoscalingUnit(
        unit_title=title,
        stack_config=network_config,
        asg_config=asg_config,
        elb_config=elb_config,
        template=template,
        dependencies=dependencies
    )
