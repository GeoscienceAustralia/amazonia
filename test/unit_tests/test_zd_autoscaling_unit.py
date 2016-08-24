from nose.tools import *
from troposphere import ec2, Ref, Template

from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.zd_autoscaling_unit import ZdAutoscalingUnit

template = elb_config = network_config = common_asg_config = block_devices_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, elb_config, network_config, common_asg_config, block_devices_config
    block_devices_config = [{
            'device_name': '/dev/xvda',
            'ebs_volume_size': '15',
            'ebs_volume_type': 'gp2',
            'ebs_encrypted': False,
            'ebs_snapshot_id': '',
            'virtual_name': False}]

    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    template = Template()

    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    private_subnets = [ec2.Subnet('MySubnet',
                                  AvailabilityZone='ap-southeast-2a',
                                  VpcId=Ref(vpc),
                                  CidrBlock='10.0.1.0/24')]
    public_subnets = [ec2.Subnet('MySubnet2',
                                 AvailabilityZone='ap-southeast-2a',
                                 VpcId=Ref(vpc),
                                 CidrBlock='10.0.2.0/24')]
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        alert=None,
        alert_emails=None,
        hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )
    nat = SingleInstance(title='Nat',
                         template=template,
                         single_instance_config=single_instance_config
                         )
    single_instance_config.is_nat = False
    single_instance_config.si_image_id = 'ami-dc361ebf'
    jump = SingleInstance(title='Jump',
                          template=template,
                          single_instance_config=single_instance_config)
    network_config = NetworkConfig(jump=jump,
                                   nat=nat,
                                   private_subnets=private_subnets,
                                   public_subnets=public_subnets,
                                   vpc=vpc,
                                   public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
                                   stack_hosted_zone_name=None,
                                   keypair='pipeline',
                                   cd_service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK')
    elb_config = ElbConfig(elb_log_bucket=None,
                           loadbalancer_protocol=['HTTP'],
                           instance_protocol=['HTTP'],
                           instanceports=['80'],
                           loadbalancerports=['80'],
                           elb_health_check='HTTP:80/index.html',
                           public_unit=True,
                           unit_hosted_zone_name=None,
                           ssl_certificate_id=None)
    common_asg_config = AsgConfig(
        minsize=1,
        maxsize=1,
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        health_check_grace_period=300,
        health_check_type='ELB',
        userdata=userdata,
        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        block_devices_config=block_devices_config)


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
    assert_equals(unit.prod_elb.trop_elb.title, 'prod' + title + 'Elb')
    assert_equals(unit.pre_elb.trop_elb.title, 'pre' + title + 'Elb')
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
                                         green_asg_config=green_asg_config)
    unit2 = create_zdtd_autoscaling_unit(unit_title='app2',
                                         blue_asg_config=blue_asg_config,
                                         green_asg_config=green_asg_config)

    unit1.add_unit_flow(receiver=unit2)
    assert_equals(len(unit1.blue_asg.egress), 3)
    assert_equals(len(unit1.green_asg.egress), 3)
    assert_equals(len(unit1.blue_asg.ingress), 3)
    assert_equals(len(unit1.green_asg.ingress), 3)
    assert_equals(len(unit1.pre_elb.ingress), 1)
    assert_equals(len(unit1.prod_elb.ingress), 1)
    assert_equals(len(unit1.pre_elb.egress), 2)
    assert_equals(len(unit1.prod_elb.egress), 2)

    assert_equals(len(unit2.blue_asg.egress), 1)
    assert_equals(len(unit2.green_asg.egress), 1)
    assert_equals(len(unit2.blue_asg.ingress), 3)
    assert_equals(len(unit2.green_asg.ingress), 3)
    assert_equals(len(unit2.pre_elb.ingress), 3)
    assert_equals(len(unit2.prod_elb.ingress), 3)
    assert_equals(len(unit2.pre_elb.egress), 2)
    assert_equals(len(unit2.prod_elb.egress), 2)


def create_zdtd_autoscaling_unit(unit_title, blue_asg_config, green_asg_config):
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
        dependencies=None,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config,
        elb_config=elb_config,
        network_config=network_config
    )
    return unit
