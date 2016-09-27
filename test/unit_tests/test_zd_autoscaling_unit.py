from amazonia.classes.amz_zd_autoscaling import ZdAutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
from network_setup import get_network_config
from nose.tools import *
from troposphere import Ref

template = elb_config = network_config = common_asg_config = block_devices_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, elb_config, network_config, common_asg_config, block_devices_config
    block_devices_config = [BlockDevicesConfig(
        device_name='/dev/xvda',
        ebs_volume_size='15',
        ebs_volume_type='gp2',
        ebs_encrypted=False,
        ebs_snapshot_id=None,
        virtual_name=False)]

    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    network_config, template = get_network_config()

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='JSESSION'
        )]

    elb_config = ElbConfig(elb_log_bucket=None,
                           elb_listeners_config=elb_listeners_config,
                           elb_health_check='HTTP:80/index.html',
                           public_unit=True,
                           ssl_certificate_id=None,
                           healthy_threshold=10,
                           unhealthy_threshold=2,
                           interval=300,
                           timeout=30)
    common_asg_config = AsgConfig(
        minsize=1,
        maxsize=1,
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        health_check_grace_period=300,
        health_check_type='ELB',
        userdata=userdata,
        iam_instance_profile_arn=None,
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None
    )


@with_setup(setup_resources)
def test_autoscaling_unit():
    """Test zdtd autoscaling unit structure"""
    global common_asg_config
    title = 'app'
    blue_asg_config = common_asg_config
    green_asg_config = common_asg_config
    unit = create_zdtd_autoscaling_unit(unit_title=title,
                                        blue_asg_config=blue_asg_config,
                                        green_asg_config=green_asg_config)
    assert_equals(unit.green_asg.trop_asg.title, 'green' + title + 'Asg')
    assert_equals(unit.blue_asg.trop_asg.title, 'blue' + title + 'Asg')
    assert_equals(unit.prod_elb.trop_elb.title, title)
    assert_equals(unit.pre_elb.trop_elb.title, 'pre' + title)
    [assert_is(type(lbn), Ref) for lbn in unit.green_asg.trop_asg.LoadBalancerNames]
    [assert_is(type(lbn), Ref) for lbn in unit.blue_asg.trop_asg.LoadBalancerNames]

    assert_equals(len(unit.blue_asg.egress), 1)
    assert_equals(len(unit.green_asg.egress), 1)
    assert_equals(len(unit.blue_asg.ingress), 3)
    assert_equals(len(unit.green_asg.ingress), 3)
    assert_equals(len(unit.prod_elb.ingress), 1)
    assert_equals(len(unit.pre_elb.ingress), 1)
    assert_equals(len(unit.prod_elb.egress), 2)
    assert_equals(len(unit.pre_elb.egress), 2)


@with_setup(setup_resources)
def test_unit_association():
    """Test zdtd autoscaling unit flow"""
    global common_asg_config
    blue_asg_config = common_asg_config

    green_asg_config = common_asg_config
    unit1 = create_zdtd_autoscaling_unit(unit_title='app1',
                                         blue_asg_config=blue_asg_config,
                                         green_asg_config=green_asg_config,
                                         dependencies=['app2:80'])
    create_zdtd_autoscaling_unit(unit_title='app2',
                                 blue_asg_config=blue_asg_config,
                                 green_asg_config=green_asg_config)

    assert_equals(len(unit1.blue_asg.egress), 2)
    assert_equals(len(unit1.green_asg.egress), 2)
    assert_equals(len(unit1.blue_asg.ingress), 3)
    assert_equals(len(unit1.green_asg.ingress), 3)
    assert_equals(len(unit1.pre_elb.ingress), 1)
    assert_equals(len(unit1.prod_elb.ingress), 1)
    assert_equals(len(unit1.pre_elb.egress), 2)
    assert_equals(len(unit1.prod_elb.egress), 2)


def create_zdtd_autoscaling_unit(unit_title, blue_asg_config, green_asg_config, dependencies=None):
    """Helper function to create unit
    :param unit_title: title of unit
    :param blue_asg_config: blue specific asg config
    :param green_asg_config: green specific asg config
    :return new zdtd_autoscaling unit
    """
    global template, elb_config, network_config
    unit = ZdAutoscalingUnit(
        unit_title=unit_title,
        template=template,
        dependencies=dependencies,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config,
        elb_config=elb_config,
        stack_config=network_config
    )
    return unit
