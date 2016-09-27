from amazonia.classes.amz_autoscaling import AutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
from network_setup import get_network_config
from nose.tools import *
from troposphere import Ref

template = network_config = elb_config = asg_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, elb_config, asg_config

    network_config, template = get_network_config()

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
        iam_instance_profile_arn=None,
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


@with_setup(setup_resources())
def test_autoscaling_unit():
    """Test autoscaling unit structure"""
    title = 'app'
    unit = create_autoscaling_unit(unit_title=title)
    assert_equals(unit.asg.trop_asg.title, title + 'Asg')
    assert_equals(unit.elb.trop_elb.title, title)
    [assert_is(type(lbn), Ref) for lbn in unit.asg.trop_asg.LoadBalancerNames]
    assert_equals(len(unit.asg.egress), 1)
    assert_equals(len(unit.asg.ingress), 2)
    assert_equals(len(unit.elb.ingress), 1)
    assert_equals(len(unit.elb.egress), 1)


@with_setup(setup_resources())
def test_unit_association():
    """Test autoscaling unit flow"""
    unit2 = create_autoscaling_unit(unit_title='app2')
    unit1 = create_autoscaling_unit(unit_title='app1', dependencies=['app2:80'])
    assert_equals(len(unit1.asg.egress), 2)
    assert_equals(len(unit1.asg.ingress), 2)
    assert_equals(len(unit1.elb.ingress), 1)
    assert_equals(len(unit1.elb.egress), 1)


def create_autoscaling_unit(unit_title, dependencies=None):
    """Helper function to create unit
    :param unit_title: title of unit
    :return new autoscaling unit
    """
    global template, network_config, asg_config, elb_config
    unit = AutoscalingUnit(
        unit_title=unit_title,
        stack_config=network_config,
        asg_config=asg_config,
        elb_config=elb_config,
        template=template,
        dependencies=dependencies
    )
    return unit
