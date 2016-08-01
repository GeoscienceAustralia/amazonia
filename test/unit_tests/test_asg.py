import troposphere.elasticloadbalancing as elb
from nose.tools import *
from troposphere import ec2, Ref, Template, Join, Base64

from amazonia.classes.asg import Asg, MalformedSNSError
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.network_config import NetworkConfig

template = asg_config = elb_config = network_config = load_balancer = None


def setup_resources():
    """
    Initialise resources before each test
    """
    global template, asg_config, elb_config, network_config, load_balancer
    template = Template()
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
        cd_service_role_arn='arn:aws:iam::12345678987654321:role/CodeDeployServiceRole',
        iam_instance_profile_arn='arn:aws:iam::12345678987654321:role/InstanceProfileRole',
        image_id='ami-dc361ebf',
        instance_type='t2.micro',
        keypair='pipeline',
        sns_topic_arn='arn:aws:sns:ap-southeast-2:1234567890:test_service_status',
        sns_notification_types=['autoscaling:EC2_INSTANCE_LAUNCH', 'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                                'autoscaling:EC2_INSTANCE_TERMINATE', 'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'],
        maxsize=1,
        minsize=1,
        hdd_size=None
    )
    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')

    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')
    network_config = NetworkConfig(
        vpc=ec2.VPC('MyVPC',
                    CidrBlock='10.0.0.0/16'),
        private_subnets=[subnet],
        public_subnets=[subnet],
        jump=None,
        nat=None,
        public_cidr=None,
        unit_hosted_zone_name=None
    )

    load_balancer = elb.LoadBalancer('testElb',
                                     CrossZone=True,
                                     HealthCheck=elb.HealthCheck(Target='HTTP:8080/error/noindex.html',
                                                                 HealthyThreshold='2',
                                                                 UnhealthyThreshold='5',
                                                                 Interval='15',
                                                                 Timeout='5'),
                                     Listeners=[elb.Listener(LoadBalancerPort='80',
                                                             Protocol='HTTP',
                                                             InstancePort='80',
                                                             InstanceProtocol='HTTP')],
                                     Scheme='internet-facing',
                                     Subnets=[subnet])


@with_setup(setup_resources)
def test_asg():
    """
    Tests correct structure of autoscaling group objects.
    """
    global asg_config
    asg_titles = ['simple', 'hard', 'harder', 'easy']

    for title in asg_titles:
        asg = create_asg(title)
        assert_equals(asg.trop_asg.title, title + 'Asg')
        assert_equals(asg.trop_asg.MinSize, 1)
        assert_equals(asg.trop_asg.MaxSize, 1)
        [assert_is(type(subnet_id), Ref) for subnet_id in asg.trop_asg.VPCZoneIdentifier]
        assert_is(type(asg.trop_asg.LaunchConfigurationName), Ref)
        assert_equals(asg.trop_asg.AvailabilityZones, ['ap-southeast-2a'])
        [assert_is(type(lbn), Ref) for lbn in asg.trop_asg.LoadBalancerNames]
        assert_equals(asg.trop_asg.HealthCheckType, 'ELB')
        assert_equals(asg.trop_asg.HealthCheckGracePeriod, 300)
        assert_not_equal(asg.trop_asg.NotificationConfigurations, None)
        assert_equals(asg.trop_asg.NotificationConfigurations[0].TopicARN,
                      'arn:aws:sns:ap-southeast-2:1234567890:test_service_status')
        assert_list_equal(asg.trop_asg.NotificationConfigurations[0].NotificationTypes,
                          ['autoscaling:EC2_INSTANCE_LAUNCH', 'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                           'autoscaling:EC2_INSTANCE_TERMINATE', 'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'])
        assert_equals(asg.lc.title, title + 'Asg' + 'Lc')
        assert_equals(asg.lc.ImageId, 'ami-dc361ebf')
        assert_equals(asg.lc.InstanceType, 't2.micro')
        assert_equals(asg.lc.KeyName, 'pipeline')
        assert_equals(asg.lc.IamInstanceProfile, 'arn:aws:iam::12345678987654321:role/InstanceProfileRole')
        assert_is(type(asg.lc.UserData), Base64)
        [assert_is(type(sg), Ref) for sg in asg.lc.SecurityGroups]
        assert_equals(asg.cd_app.title, title + 'Asg' + 'Cda')
        assert_is(type(asg.cd_app.ApplicationName), Join)
        assert_is(type(asg.cd_deploygroup.ApplicationName), Ref)
        assert_equals(asg.cd_deploygroup.title, title + 'Asg' + 'Cdg')
        assert_is(type(asg.cd_deploygroup.DeploymentGroupName), Join)
        [assert_is(type(cdasg), Ref) for cdasg in asg.cd_deploygroup.AutoScalingGroups]
        assert_equals(asg.cd_deploygroup.ServiceRoleArn, 'arn:aws:iam::12345678987654321:role/CodeDeployServiceRole')


@with_setup(setup_resources)
def test_no_cd_group_and_no_sns():
    """
    Test that an asg is created without a CD and without an SNS topic
    """
    global template, load_balancer, network_config, asg_config
    asg_config.cd_service_role_arn = None
    asg = Asg(
        title='noCdSns',
        template=template,
        load_balancers=[load_balancer],
        asg_config=asg_config,
        network_config=network_config
    )
    assert_is_none(asg.cd_app)
    assert_is_none(asg.cd_deploygroup)


@with_setup(setup_resources)
def test_no_userdata():
    """
    Tests that an empty userdata is correctly handled
    """

    global asg_config
    asg_config.userdata = None

    asg = create_asg('nouserdata')

    assert_equals(asg.lc.UserData, '')


@with_setup(setup_resources)
def test_change_hdd_size():
    """
    Tests that the EBS volumesize can be confirgured correctly using hdd_size
    """
    global asg_config
    asg_config.hdd_size = '50'
    asg = create_asg('hddsize')

    assert_equals(asg.lc.BlockDeviceMappings[0].Ebs.VolumeSize, '50')


@with_setup(setup_resources)
def test_malformed_sns():
    """
    Test that an asg raises an error if SNS parameters are passed in malformed
    """
    global template, network_config, asg_config

    asg_config.sns_notification_types = None
    assert_raises(MalformedSNSError, Asg, **{'title': 'testsns',
                                             'template': template,
                                             'load_balancers': [load_balancer],
                                             'network_config': network_config,
                                             'asg_config': asg_config
                                             })


def create_asg(title):
    """
    Helper function to create ASG Troposhpere object.
    :param title: Title of autoscaling group to create
    :return: Troposphere object for single instance, security group and output
    """
    global template, load_balancer, network_config, asg_config
    asg = Asg(
        title=title,
        template=template,
        load_balancers=[load_balancer],
        network_config=network_config,
        asg_config=asg_config
    )

    return asg
