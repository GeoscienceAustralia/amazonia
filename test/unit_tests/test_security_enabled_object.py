#!/usr/bin/python3

from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject
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

    vpc = Ref(template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16',
                                        EnableDnsSupport='true',
                                        EnableDnsHostnames='true')))


@with_setup(setup_resources)
def test_security_enabled_object():
    """
    Test title, security group title, template
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)

    assert_equals(myobj.title, 'Unit01Web')
    assert_equals(myobj.trop_security_group.title, 'Unit01WebSg')
    assert_equals(myobj.template, template)


@with_setup(setup_resources)
def test_create_sg():
    """
    Test security group title, Group Description
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)

    assert_equals(myobj.trop_security_group.title, 'Unit01WebSg')
    assert_equals(myobj.trop_security_group.GroupDescription, 'Security group')
    assert_is(type(myobj.trop_security_group.VpcId), Ref)


@with_setup(setup_resources)
def test_add_flow():
    """
    Test ingress and egress rules are correctly applied betwen two security groups
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)
    otherobj = LocalSecurityEnabledObject(title='Unit02Web', vpc=vpc, template=template)

    myobj.add_flow(otherobj, '80')

    assert_equals(otherobj.ingress[0].title, 'Unit02Web80FromUnit01Web80')
    assert_equals(otherobj.ingress[0].IpProtocol, 'tcp')
    assert_equals(otherobj.ingress[0].FromPort, '80')
    assert_equals(otherobj.ingress[0].ToPort, '80')

    assert_equals(myobj.egress[0].title, 'Unit01Web80ToUnit02Web80')
    assert_equals(myobj.egress[0].IpProtocol, 'tcp')
    assert_equals(myobj.egress[0].FromPort, '80')
    assert_equals(myobj.egress[0].ToPort, '80')


@with_setup(setup_resources)
def test_add_ingress():
    """
    Test ingress rules are correctly applied to security group
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)
    otherobj = LocalSecurityEnabledObject(title='Unit02Web', vpc=vpc, template=template)

    myobj.add_ingress(otherobj, '80')

    myobj.add_ingress(otherobj, '-1')

    assert_equals(myobj.ingress[0].title, 'Unit01Web80FromUnit02Web80')
    assert_equals(myobj.ingress[0].IpProtocol, 'tcp')
    assert_equals(myobj.ingress[0].FromPort, '80')
    assert_equals(myobj.ingress[0].ToPort, '80')
    assert_equals(myobj.ingress[1].title, 'Unit01WebAllFromUnit02WebAll')
    assert_equals(myobj.ingress[1].IpProtocol, 'tcp')
    assert_equals(myobj.ingress[1].FromPort, '0')
    assert_equals(myobj.ingress[1].ToPort, '65535')


@with_setup(setup_resources)
def test_add_egress():
    """
    Test egress rules are correctly applied to security group
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)
    otherobj = LocalSecurityEnabledObject(title='Unit02Web', vpc=vpc, template=template)

    myobj.add_egress(otherobj, '80')

    myobj.add_egress(otherobj, '-1')

    assert_equals(myobj.egress[0].title, 'Unit01Web80ToUnit02Web80')
    assert_equals(myobj.egress[0].IpProtocol, 'tcp')
    assert_equals(myobj.egress[0].FromPort, '80')
    assert_equals(myobj.egress[0].ToPort, '80')
    assert_equals(myobj.egress[1].title, 'Unit01WebAllToUnit02WebAll')
    assert_equals(myobj.egress[1].IpProtocol, 'tcp')
    assert_equals(myobj.egress[1].FromPort, '0')
    assert_equals(myobj.egress[1].ToPort, '65535')


@with_setup(setup_resources)
def test_add_ip_ingress():
    """
    Test ingress rules are correctly applied to CIDRs, elbs, single instances (nat or jump)
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)

    cidrs = [{'name': 'GA1', 'cidr': '123.123.132.123/24'},
             {'name': 'GA2', 'cidr': '321.321.321.321/32'},
             {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}]

    allcidr = {'name': 'All', 'cidr': '0.0.0.0/0'}

    for num, cidr in enumerate(cidrs):
        myobj.add_ingress(cidr, port='80')
        assert_equals(myobj.ingress[num].title, 'Unit01Web80From{0}80'.format(cidr['name']))
        assert_equals(myobj.ingress[num].IpProtocol, 'tcp')
        assert_equals(myobj.ingress[num].FromPort, '80')
        assert_equals(myobj.ingress[num].ToPort, '80')

    myobj.add_ingress(sender=allcidr, port='-1')

    assert_equals(myobj.ingress[3].title, 'Unit01WebAllFrom{0}All'.format(allcidr['name']))
    assert_equals(myobj.ingress[3].IpProtocol, 'tcp')
    assert_equals(myobj.ingress[3].FromPort, '0')
    assert_equals(myobj.ingress[3].ToPort, '65535')


@with_setup(setup_resources)
def test_add_ip_egress():
    """
    Test egress rules are correctly applied to CIDRs, elbs, single instances (nat or jump)
    """
    myobj = LocalSecurityEnabledObject(title='Unit01Web', vpc=vpc, template=template)

    cidrs = [{'name': 'GA1', 'cidr': '123.123.132.123/24'},
             {'name': 'GA2', 'cidr': '321.321.321.321/32'},
             {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}]

    allcidr = {'name': 'All', 'cidr': '0.0.0.0/0'}

    for num, cidr in enumerate(cidrs):
        myobj.add_egress(cidr, port='80')
        assert_equals(myobj.egress[num].title, 'Unit01Web80To{0}80'.format(cidr['name']))
        assert_equals(myobj.egress[num].IpProtocol, 'tcp')
        assert_equals(myobj.egress[num].FromPort, '80')
        assert_equals(myobj.egress[num].ToPort, '80')

    myobj.add_egress(receiver=allcidr, port='-1')

    assert_equals(myobj.egress[3].title, 'Unit01WebAllTo{0}All'.format(allcidr['name']))
    assert_equals(myobj.egress[3].IpProtocol, 'tcp')
    assert_equals(myobj.egress[3].FromPort, '0')
    assert_equals(myobj.egress[3].ToPort, '65535')
