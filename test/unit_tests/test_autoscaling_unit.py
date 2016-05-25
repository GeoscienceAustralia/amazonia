from nose.tools import *
from troposphere import ec2, Ref, Template

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.autoscaling_unit import AutoscalingUnit

userdata = template = vpc = private_subnets = public_subnets = nat = jump = health_check_grace_period = \
    health_check_type = None


def setup_resources():
    """ Setup global variables between tests"""
    global userdata, template, vpc, private_subnets, public_subnets, nat, jump, health_check_grace_period, \
        health_check_type
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
                         si_image_id='ami-162c0c75',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         template=template)
    jump = SingleInstance(title='Jump',
                          keypair='pipeline',
                          si_image_id='ami-162c0c75',
                          si_instance_type='t2.nano',
                          vpc=vpc,
                          subnet=public_subnets[0],
                          template=template)

    health_check_grace_period = 300
    health_check_type = 'ELB'


@with_setup(setup_resources())
def test_autoscaling_unit():
    """Test autoscaling unit structure"""
    title = 'app'
    unit = create_autoscaling_unit(unit_title=title)
    assert_equals(unit.asg.trop_asg.title, title + 'Asg')
    assert_equals(unit.elb.trop_elb.title, title + 'Elb')
    [assert_is(type(lbn), Ref) for lbn in unit.asg.trop_asg.LoadBalancerNames]
    assert_equals(len(unit.asg.egress), 2)
    assert_equals(len(unit.asg.ingress), 2)
    assert_equals(len(unit.elb.ingress), 1)
    assert_equals(len(unit.elb.egress), 1)


@with_setup(setup_resources())
def test_unit_association():
    """Test autoscaling unit flow"""
    unit1 = create_autoscaling_unit(unit_title='app1')
    unit2 = create_autoscaling_unit(unit_title='app2')
    unit1.add_unit_flow(receiver=unit2)
    assert_equals(len(unit1.asg.egress), 3)
    assert_equals(len(unit1.asg.ingress), 2)
    assert_equals(len(unit1.elb.ingress), 1)
    assert_equals(len(unit1.elb.egress), 1)

    assert_equals(len(unit2.asg.egress), 2)
    assert_equals(len(unit2.asg.ingress), 2)
    assert_equals(len(unit2.elb.ingress), 2)
    assert_equals(len(unit2.elb.egress), 1)


def create_autoscaling_unit(unit_title):
    """Helper function to create unit
    :param unit_title: title of unit
    :return new autoscaling unit
    """
    global userdata, template, vpc, private_subnets, public_subnets, nat, jump, health_check_grace_period, \
        health_check_type
    unit = AutoscalingUnit(
        unit_title=unit_title,
        vpc=vpc,
        template=template,
        protocols=['HTTP'],
        instanceports=['80'],
        loadbalancerports=['80'],
        path2ping='index.html',
        public_subnets=public_subnets,
        private_subnets=private_subnets,
        public_cidr={'name': 'PublicIp','cidr': '0.0.0.0/0'},
        minsize=1,
        maxsize=1,
        keypair='pipeline',
        image_id='ami-05446966',
        instance_type='t2.nano',
        health_check_grace_period=health_check_grace_period,
        health_check_type=health_check_type,
        userdata=userdata,
        cd_service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        iam_instance_profile_arn=None,
        nat=nat,
        jump=jump,
        hosted_zone_name=None,
        gateway_attachment='testIgAtch',
        elb_log_bucket=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        dependencies=None
    )
    return unit
