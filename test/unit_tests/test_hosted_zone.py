#!/usr/bin/python3

from amazonia.classes.hosted_zone import HostedZone
from nose.tools import *
from troposphere import Template, ec2, Ref

template = vpc = None


def setup_resources():
    """
    Create generic testing data
    """
    global template
    global vpc

    template = Template()

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16',
                                        EnableDnsSupport='true',
                                        EnableDnsHostnames='true'))


def create_hosted_zone(domain, vpcs=None):
    """
    Creates a hosted zone using the Amazonia class for testing.
    :param domain: the domain to give the hosted zone
    :param vpcs: a list of vpcs to attach the hosted zone to (making it private)
    :return: A hosted zone object created from the amazonia class
    """

    return HostedZone(template=template, domain=domain, vpcs=vpcs)


@with_setup(setup_resources)
def test_public_hosted_zone():
    """
    Tests creation of a public hosted zone.
    """

    domain = 'public.domain.'

    hz = create_hosted_zone(domain)

    assert_equals(hz.trop_hosted_zone.Name, domain)


@with_setup(setup_resources)
def test_private_hosted_zone():
    """
    Tests creation of a private hosted zone.
    """

    global vpc

    domain = 'private.domain.'

    hz = create_hosted_zone(domain, [Ref(vpc)])

    assert_equals(type(hz.trop_hosted_zone.VPCs), type([]))
    assert_equals(hz.trop_hosted_zone.Name, domain)
