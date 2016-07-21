#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, ec2
from amazonia.classes.single_instance import SingleInstance


def test_nat_single_instance():
    """
    Tests for creation of a nat instance and expects natting (SourceDestCheck)
    to be enabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """

    si = create_si('nat', is_nat=True)
    si_sdc = si.single.SourceDestCheck
    assert_equals(si_sdc, 'false')
    sio = si.template.outputs['nat'].Description
    assert_in('PrivateIp', sio)
    assert_equals(si.single.IamInstanceProfile, 'instance-profile')


def test_not_nat_single_instance():
    """
    Tests for instances where 'nat' is NOT the first 3 letters  of the title and expect natting (SourceDestCheck)
    to be disabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """
    jump_titles = ['jump', 'Jump', '2Jump', 'other', 'natjump', 'testStackJump']

    for title in jump_titles:
        si = create_si(title)
        si_sdc = si.single.SourceDestCheck
        assert_equals(si_sdc, 'true')
        sio = si.template.outputs[title].Description
        assert_in('PublicIp', sio)
        assert_equals(si.single.IamInstanceProfile, 'instance-profile')


def test_jump_with_hostedzone_creates_r53_record():
    """
    Tests that creating a jump host and supplying a hostedzone creates an elastic IP, r53 recordset and output for
    the jump host
    :return: Pass
    """
    jump_titles = ['jump1', 'jump2']

    for title in jump_titles:
        si = create_si(title)

        assert_equals(si.eip_address.Domain, 'vpc')
        assert_equals(si.si_r53.HostedZoneName, 'my.hostedzone.')

        sio = si.template.outputs[title + 'URL'].Value
        assert_equals(sio, si.si_r53.Name)


def create_si(title, is_nat=False):
    """
    Helper function to create Single instance Troposhpere object to interate through.
    :param title: name of instance
    :param is_nat: is the instance a nat
    :return: Troposphere object for single instance, security group and output
    """
    vpc = 'vpc-12345'
    dependencies = 'igw-12345'
    hosted_zone_name = None if is_nat else 'my.hostedzone.'
    template = Template()
    subnet = template.add_resource(ec2.Subnet('subnet12345',
                                              AvailabilityZone='ap-southeast-2a',
                                              VpcId=vpc,
                                              CidrBlock='10.0.1.0/24'))
    si = SingleInstance(title=title,
                        keypair='pipeline',
                        si_image_id='ami-53371f30',
                        si_instance_type='t2.nano',
                        vpc=vpc,
                        subnet=subnet,
                        hosted_zone_name=hosted_zone_name,
                        instance_dependencies=dependencies,
                        template=template,
                        is_nat=is_nat,
                        iam_instance_profile_arn='my/instance-profile')
    return si
