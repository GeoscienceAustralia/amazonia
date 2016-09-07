#!/usr/bin/python3

from amazonia.classes.hosted_zone import HostedZone
from nose.tools import *
from troposphere import Template, ec2
from troposphere import elasticloadbalancing as elb

template = vpc = ec2_instance = my_elb = None


def setup_resources():
    """
    Create generic testing data
    """
    global template
    global vpc
    global ec2_instance
    global my_elb

    template = None
    template = Template()

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16',
                                        EnableDnsSupport='true',
                                        EnableDnsHostnames='true'))

    ec2_instance = template.add_resource(ec2.Instance(
        'myinstance',
        KeyName='INSERT_YOUR_KEYPAIR_HERE',
        ImageId='ami-12345',
        InstanceType='t2.nano',
        NetworkInterfaces=[ec2.NetworkInterfaceProperty(GroupSet=['sg-12345'],
                                                        AssociatePublicIpAddress=True,
                                                        DeviceIndex='0',
                                                        DeleteOnTermination=True,
                                                        SubnetId='subnet-12345')],
        SourceDestCheck=True,
        DependsOn='igw-12345'
    ))

    my_elb = template.add_resource(elb.LoadBalancer('myLoadBalancer',
                                                    CrossZone=True,
                                                    HealthCheck=elb.HealthCheck(Target='HTTP:80/index.html',
                                                                                HealthyThreshold='10',
                                                                                UnhealthyThreshold='2',
                                                                                Interval='300',
                                                                                Timeout='60'),
                                                    Listeners=[elb.Listener(LoadBalancerPort='80',
                                                                            Protocol='HTTP',
                                                                            InstancePort='80',
                                                                            InstanceProtocol='HTTP')],
                                                    Scheme='internet-facing',
                                                    SecurityGroups=['sg-12345'],
                                                    Subnets=['subnet-12345']
                                                    ))


def create_hosted_zone(domain, vpcs=None):
    """
    Creates a hosted zone using the Amazonia class for testing.
    :param domain: the domain to give the hosted zone
    :param vpcs: a list of vpcs to attach the hosted zone to (making it private)
    :return: A hosted zone object created from the amazonia class
    """

    return HostedZone(template=template, domain=domain, vpcs=vpcs)


def test_public_hosted_zone():
    """
    Tests creation of a public hosted zone.
    """

    domain = 'public.domain.'

    hz = create_hosted_zone(domain)

    assert_equals(hz.trop_hosted_zone.Name, domain)


@with_setup(setup_resources())
def test_private_hosted_zone():
    """
    Tests creation of a private hosted zone.
    """

    global vpc

    domain = 'private.domain.'

    hz = create_hosted_zone(domain, [vpc])

    assert_equals(type(hz.trop_hosted_zone.VPCs), type([]))
    assert_equals(hz.trop_hosted_zone.Name, domain)
