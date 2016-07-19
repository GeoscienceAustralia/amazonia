#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, ec2, GetAtt, route53
from troposphere import elasticloadbalancing as elb

from amazonia.classes.hosted_zone import HostedZone, BadTargetError

template = domain = title = vpc = ec2_instance = my_elb = None


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


def create_hosted_zone(domain, title, vpcs=None):
    """
    Creates a hosted zone using the Amazonia class for testing.
    :param domain: the domain to give the hosted zone
    :param title: the title to give the created hosted zone
    :param vpcs: a list of vpcs to attach the hosted zone to (making it private)
    :return: A hosted zone object created from the amazonia class
    """

    return HostedZone(template=template, domain=domain, title=title, vpcs=vpcs)


def test_public_hosted_zone():
    """
    Tests creation of a public hosted zone.
    """
    global domain
    global title

    title = 'public'
    domain = '{0}.domain'.title()

    hz = create_hosted_zone(domain, title)

    assert_equals(hz.trop_hosted_zone.title, title)
    assert_equals(hz.trop_hosted_zone.Name, domain)


@with_setup(setup_resources())
def test_private_hosted_zone():
    """
    Tests creation of a private hosted zone.
    """
    global domain
    global title
    global vpc

    title = 'private'
    domain = '{0}.domain'.title()

    hz = create_hosted_zone(domain, title, [vpc])

    assert_equals(type(hz.trop_hosted_zone.VPCs), type([]))
    assert_equals(hz.trop_hosted_zone.title, title)
    assert_equals(hz.trop_hosted_zone.Name, domain)


@with_setup(setup_resources())
def test_add_record_sets():
    """
    Tests the addition of record sets with various configurations.
    """

    global domain
    global title
    global vpc
    global ec2_instance
    global my_elb

    title = 'public1'
    domain = '{0}.domain'.title()

    pub_hz = create_hosted_zone(domain, title)
    pub_hz.add_record_set('instance', ip=GetAtt(ec2_instance, 'PublicIp'))
    pub_hz.add_record_set('elb', elb=my_elb)

    aliastarget = pub_hz.recordsets[1].AliasTarget

    assert_equals(pub_hz.recordsets[0].title, 'instance')
    assert_equals(pub_hz.recordsets[1].title, 'elb')
    assert_equals(pub_hz.recordsets[0].Type, 'A')
    assert_equals(pub_hz.recordsets[1].Type, 'A')
    assert_equals(type(pub_hz.recordsets[0].ResourceRecords[0]), type(GetAtt(ec2_instance, 'PublicIp')))
    assert_equals(pub_hz.recordsets[0].TTL, '300')
    assert_equals(type(aliastarget), type(route53.AliasTarget(dnsname=GetAtt(elb, 'DNSName'),
                                                              hostedzoneid=GetAtt(elb, 'CanonicalHostedZoneNameID'))))
    assert_raises(BadTargetError, pub_hz.add_record_set, **{'title': 'notarget'})
    assert_raises(BadTargetError, pub_hz.add_record_set, **{'title': 'toomanytargets',
                                                            'ip': GetAtt(ec2_instance, 'PublicIp'),
                                                            'elb': my_elb
                                                            })
