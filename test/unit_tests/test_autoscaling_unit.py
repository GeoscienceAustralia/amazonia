from nose.tools import *
from troposphere import ec2, Ref, Template

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.autoscaling_unit import AutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig

template = network_config = elb_config = asg_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, elb_config, asg_config

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
        alert=False,
        alert_emails=['some@email.com'],
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
                          single_instance_config=single_instance_config
                          )

    network_config = NetworkConfig(
        vpc=vpc,
        private_subnets=private_subnets,
        public_subnets=public_subnets,
        nat=nat,
        jump=jump,
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        stack_hosted_zone_name=None,
        cd_service_role_arn='instance-iam-role-InstanceProfile-OGL42SZSIQRK',
        keypair='pipeline'
    )

    block_devices_config = [
        BlockDevicesConfig(
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
        sns_topic_arn=None,
        sns_notification_types=None,
        block_devices_config=block_devices_config
    )
    elb_config = ElbConfig(
        protocols=['HTTP'],
        instanceports=['80'],
        loadbalancerports=['80'],
        path2ping='index.html',
        elb_log_bucket=None,
        public_unit=True,
        unit_hosted_zone_name=None
    )


@with_setup(setup_resources())
def test_autoscaling_unit():
    """Test autoscaling unit structure"""
    title = 'app'
    unit = create_autoscaling_unit(unit_title=title)
    assert_equals(unit.asg.trop_asg.title, title + 'Asg')
    assert_equals(unit.elb.trop_elb.title, title + 'Elb')
    [assert_is(type(lbn), Ref) for lbn in unit.asg.trop_asg.LoadBalancerNames]
    assert_equals(len(unit.asg.egress), 1)
    assert_equals(len(unit.asg.ingress), 2)
    assert_equals(len(unit.elb.ingress), 1)
    assert_equals(len(unit.elb.egress), 1)


@with_setup(setup_resources())
def test_unit_association():
    """Test autoscaling unit flow"""
    unit1 = create_autoscaling_unit(unit_title='app1')
    unit2 = create_autoscaling_unit(unit_title='app2')
    unit1.add_unit_flow(receiver=unit2)
    assert_equals(len(unit1.asg.egress), 2)
    assert_equals(len(unit1.asg.ingress), 2)
    assert_equals(len(unit1.elb.ingress), 1)
    assert_equals(len(unit1.elb.egress), 1)

    assert_equals(len(unit2.asg.egress), 1)
    assert_equals(len(unit2.asg.ingress), 2)
    assert_equals(len(unit2.elb.ingress), 2)
    assert_equals(len(unit2.elb.egress), 1)


def create_autoscaling_unit(unit_title):
    """Helper function to create unit
    :param unit_title: title of unit
    :return new autoscaling unit
    """
    global template, network_config, asg_config, elb_config
    unit = AutoscalingUnit(
        unit_title=unit_title,
        network_config=network_config,
        asg_config=asg_config,
        elb_config=elb_config,
        template=template,
        dependencies=None
    )
    return unit
