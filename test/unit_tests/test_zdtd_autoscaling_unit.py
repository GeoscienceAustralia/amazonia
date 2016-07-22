from nose.tools import *
from troposphere import ec2, Ref, Template

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.zdtd_autoscaling_unit import ZdtdAutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig

template = elb_config = network_config = common_asg_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, elb_config, network_config, common_asg_config
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
    nat = SingleInstance(title='Nat',
                         keypair='pipeline',
                         si_image_id='ami-53371f30',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         template=template,
                         instance_dependencies=vpc.title)
    jump = SingleInstance(title='Jump',
                          keypair='pipeline',
                          si_image_id='ami-dc361ebf',
                          si_instance_type='t2.nano',
                          vpc=vpc,
                          subnet=public_subnets[0],
                          template=template,
                          instance_dependencies=vpc.title)
    network_config = NetworkConfig(jump=jump, nat=nat, private_subnets=private_subnets, public_subnets=public_subnets,
                                   vpc=vpc, public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
                                   unit_hosted_zone_name=None)
    elb_config = ElbConfig(elb_log_bucket=None, protocols=['HTTP'],
                           instanceports=['80'],
                           loadbalancerports=['80'], path2ping='index.html', public_unit=True)
    common_asg_config = AsgConfig(
        minsize=1,
        maxsize=1,
        keypair='pipeline',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        health_check_grace_period=300,
        health_check_type='ELB',
        userdata=userdata,
        cd_service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        hdd_size=8)


@with_setup(setup_resources())
def test_autoscaling_unit():
    """Test zdtd autoscaling unit structure"""
    title = 'app'
    blue_asg_config = AsgConfig(minsize=None,
                                maxsize=None,
                                keypair=None,
                                image_id=None,
                                instance_type=None,
                                health_check_grace_period=None,
                                health_check_type=None,
                                userdata=None,
                                cd_service_role_arn=None,
                                iam_instance_profile_arn=None,
                                sns_topic_arn=None,
                                sns_notification_types=None,
                                hdd_size=None)
    green_asg_config = AsgConfig(minsize=None,
                                 maxsize=None,
                                 keypair=None,
                                 image_id=None,
                                 instance_type=None,
                                 health_check_grace_period=None,
                                 health_check_type=None,
                                 userdata=None,
                                 cd_service_role_arn=None,
                                 iam_instance_profile_arn=None,
                                 sns_topic_arn=None,
                                 sns_notification_types=None,
                                 hdd_size=None)
    unit = create_zdtd_autoscaling_unit(unit_title=title, blue_asg_config=blue_asg_config,
                                        green_asg_config=green_asg_config,
                                        zdtd_state='blue')
    assert_equals(unit.green_asg.trop_asg.title, 'green' + title + 'Asg')
    assert_equals(unit.blue_asg.trop_asg.title, 'blue' + title + 'Asg')
    assert_equals(unit.prod_elb.trop_elb.title, 'active' + title + 'Elb')
    assert_equals(unit.test_elb.trop_elb.title, 'inactive' + title + 'Elb')
    [assert_is(type(lbn), Ref) for lbn in unit.green_asg.trop_asg.LoadBalancerNames]
    [assert_is(type(lbn), Ref) for lbn in unit.blue_asg.trop_asg.LoadBalancerNames]

    assert_equals(len(unit.blue_asg.egress), 1)
    assert_equals(len(unit.green_asg.egress), 1)
    assert_equals(len(unit.blue_asg.ingress), 2)
    assert_equals(len(unit.green_asg.ingress), 2)
    assert_equals(len(unit.prod_elb.ingress), 1)
    assert_equals(len(unit.test_elb.ingress), 1)
    assert_equals(len(unit.prod_elb.egress), 1)
    assert_equals(len(unit.test_elb.egress), 1)


@with_setup(setup_resources())
def test_unit_association():
    """Test zdtd autoscaling unit flow"""
    blue_asg_config = AsgConfig(minsize=None,
                                maxsize=None,
                                keypair=None,
                                image_id=None,
                                instance_type=None,
                                health_check_grace_period=None,
                                health_check_type=None,
                                userdata=None,
                                cd_service_role_arn=None,
                                iam_instance_profile_arn=None,
                                sns_topic_arn=None,
                                sns_notification_types=None,
                                hdd_size=None)

    green_asg_config = AsgConfig(minsize=None,
                                 maxsize=None,
                                 keypair=None,
                                 image_id=None,
                                 instance_type=None,
                                 health_check_grace_period=None,
                                 health_check_type=None,
                                 userdata=None,
                                 cd_service_role_arn=None,
                                 iam_instance_profile_arn=None,
                                 sns_topic_arn=None,
                                 sns_notification_types=None,
                                 hdd_size=None)
    unit1 = create_zdtd_autoscaling_unit(unit_title='app1', zdtd_state='green', blue_asg_config=blue_asg_config,
                                         green_asg_config=green_asg_config)
    unit2 = create_zdtd_autoscaling_unit(unit_title='app2', zdtd_state='blue', blue_asg_config=blue_asg_config,
                                         green_asg_config=green_asg_config)
    unit3 = create_zdtd_autoscaling_unit(unit_title='app3', zdtd_state='both', blue_asg_config=blue_asg_config,
                                         green_asg_config=green_asg_config)
    unit1.add_unit_flow(receiver=unit2)
    assert_equals(len(unit1.blue_asg.egress), 3)
    assert_equals(len(unit1.green_asg.egress), 3)
    assert_equals(len(unit1.blue_asg.ingress), 2)
    assert_equals(len(unit1.green_asg.ingress), 2)
    assert_equals(len(unit1.test_elb.ingress), 1)
    assert_equals(len(unit1.prod_elb.ingress), 1)
    assert_equals(len(unit1.test_elb.egress), 1)
    assert_equals(len(unit1.prod_elb.egress), 1)

    assert_equals(len(unit2.blue_asg.egress), 1)
    assert_equals(len(unit2.green_asg.egress), 1)
    assert_equals(len(unit2.blue_asg.ingress), 2)
    assert_equals(len(unit2.green_asg.ingress), 2)
    assert_equals(len(unit2.test_elb.ingress), 3)
    assert_equals(len(unit2.prod_elb.ingress), 3)
    assert_equals(len(unit2.test_elb.egress), 1)
    assert_equals(len(unit2.prod_elb.egress), 1)

    assert_equals(len(unit3.blue_asg.egress), 1)
    assert_equals(len(unit3.green_asg.egress), 1)
    assert_equals(len(unit3.blue_asg.ingress), 3)
    assert_equals(len(unit3.green_asg.ingress), 3)
    assert_equals(len(unit3.test_elb.ingress), 1)
    assert_equals(len(unit3.prod_elb.ingress), 1)
    assert_equals(len(unit3.test_elb.egress), 2)
    assert_equals(len(unit3.prod_elb.egress), 2)


def create_zdtd_autoscaling_unit(unit_title, zdtd_state, blue_asg_config, green_asg_config):
    """Helper function to create unit
    :param unit_title: title of unit
    :param zdtd_state: zdtd_state of of zdtd autoscaling unit
    :param blue_asg_config: blue specific asg config
    :param green_asg_config: green specific asg config
    :return new zdtd_autoscaling unit
    """
    global template, elb_config, network_config, common_asg_config
    unit = ZdtdAutoscalingUnit(
        unit_title=unit_title,
        template=template,
        dependencies=None,
        zdtd_state=zdtd_state,
        common_asg_config=common_asg_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config,
        elb_config=elb_config,
        network_config=network_config
    )
    return unit
