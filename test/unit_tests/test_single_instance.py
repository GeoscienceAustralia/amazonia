#!/usr/bin/python3

from nose.tools import *
from troposphere import Template
from amazonia.classes.single_instance import SingleInstance


def test_nat_single_instance():
    """
    Tests for creation of a nat instance and expects natting (SourceDestCheck)
    to be enabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """

    si = create_si('nat', is_nat=True)
    si_sdc = si.single.SourceDestCheck
    print('SourceDestCheck='.format(si_sdc))
    assert_equals(si_sdc, 'false')
    sio = si.template.outputs['nat'].Description
    print(sio)
    assert_in('PrivateIp', sio)


def test_not_nat_single_instance():
    """
    Tests for instances where 'nat' is NOT the first 3 letters  of the title and expect natting (SourceDestCheck)
    to be disabled and the PrivateIp to be displayed in the output.
    :return: Pass
    """
    jump_titles = ['jump', 'Jump', '2Jump', 'other', 'natjump', 'testStackJump']

    for title in jump_titles:
        si = create_si(title)
        print('title={0}'.format(si.title))
        si_sdc = si.single.SourceDestCheck
        print('SourceDestCheck='.format(si_sdc))
        assert_equals(si_sdc, 'true')

        sio = si.template.outputs[title].Description
        print(sio)
        assert_in('PublicIp', sio)


def create_si(title, is_nat=False):
    """
    Helper function to create Single instance Troposhpere object to interate through.
    :param title: name of instance
    :return: Troposphere object for single instance, security group and output
    """
    vpc = 'vpc-12345'
    subnet = 'subnet-123456'
    template = Template()
    si = SingleInstance(title=title,
                        keypair='pipeline',
                        si_image_id='ami-162c0c75',
                        si_instance_type='t2.nano',
                        vpc=vpc,
                        subnet=subnet,
                        template=template,
                        is_nat=is_nat)
    return si
