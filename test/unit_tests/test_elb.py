#!/usr/bin/python3

import re
from nose.tools import *
from troposphere import Template, Ref

from amazonia.classes.elb import Elb


def create_elb(instanceport='80', loadbalancerport='80', protocol='HTTP', hosted_zone_name=None, path2ping='index.html',
               elb_log_bucket=None):
    """
    Helper function to create Elb Troposhpere object to interate through.
    :param instanceport - port for traffic to instances from the load balancer
    :param loadbalancerport - port for traffic to the load balancer from public
    :param protocol: protocol for traffic
    :param path2ping: path to test page
    :param elb_log_bucket: S3 bucket to log access log to
    :param hosted_zone_name: Route53 hosted zone ID
    :return: Troposphere object for Elb,
    """
    vpc = 'vpc-12345'
    pub_sub_list = ['subnet-123456', 'subnet-123496', 'subnet-123454']
    elb = Elb(title='elb',
              instanceports=[instanceport],
              loadbalancerports=[loadbalancerport],
              subnets=pub_sub_list,
              protocols=[protocol],
              vpc=vpc,
              hosted_zone_name=hosted_zone_name,
              path2ping=path2ping,
              template=Template(),
              elb_log_bucket=elb_log_bucket,
              gateway_attachment='testIgAtch')
    return elb


def test_protocol():
    """
    Test to check that 'protocol' inputs match the beginning of Target Address
    e.g. HTTP matches HTTP:80/index.html
    Also tests that protocol matches Listener Protocol and Instance Protocol
    """
    protocols = ['HTTP', 'HTTPS', 'TCP', 'SSL']

    def helper_test_protocol(protocol_list):
        for protocol in protocol_list:
            helper_elb = create_elb(protocol=protocol)
            assert_true(re.match(protocol, helper_elb.trop_elb.HealthCheck.Target))
            for listener in helper_elb.trop_elb.Listeners:
                assert_equal(protocol, listener.Protocol)
                assert_equal(protocol, listener.InstanceProtocol)

    helper_test_protocol(protocols)


def test_target():
    """
    Tests to make sure that inputs of 'protocol', 'instanceport' and 'path2ping' correctly forms target healthcheck url
    """
    helper_elb = create_elb(protocol='HTTPS',
                            instanceport='443',
                            path2ping='/test/index.html')
    assert_equals('HTTPS:443/test/index.html', helper_elb.trop_elb.HealthCheck.Target)


def test_instance_ports():
    """
    Tests to validate that passing 'instanceport' correctly sets the instanceport in the Listener object of the ELB
    as well as the Health check target.
    'HealthCheck.Target', 'Listeners.InstancePort'
    """
    ports = ['8080', '80', '443', '5678', '-1', '99', '65535']

    for port in ports:
        helper_elb = create_elb(instanceport=port)
        assert_in(port, helper_elb.trop_elb.HealthCheck.Target)
        for listener in helper_elb.trop_elb.Listeners:
            assert_equal(port, listener.InstancePort)


def test_loadbalancer_ports():
    """
    Tests to validate that passing 'loadbalancerport' correctly sets the loadbalancer port for the Listener on the ELB
    'Listener.LoadBalancerPort'
    """
    ports = ['8080', '80', '443', '5678', '-1', '99', '65535']

    for port in ports:
        helper_elb = create_elb(loadbalancerport=port)
        for listener in helper_elb.trop_elb.Listeners:
            assert_equal(port, listener.LoadBalancerPort)


def test_subnets():
    """
    Tests to check list of subnets returns list of Refs to subnets
    e.g. [subnet1, subnet2] creates [Ref(subnet1), Ref(subnet2)]
    """
    helper_elb = create_elb()
    for subnet in helper_elb.trop_elb.Subnets:
        assert_equals(type(subnet), Ref)


def test_security_group():
    """
    Test to assert type of SecurityGroup equals Ref
    """
    helper_elb = create_elb()
    print('type = {0}'.format(type(helper_elb.trop_elb.SecurityGroups)))
    print('typeref = {0}'.format(Ref))
    for sg in helper_elb.trop_elb.SecurityGroups:
        assert_is(type(sg), Ref)


def test_hosted_zone_name():
    """
    Test route 53 record is created when hosted_zone_name is supplied
    """
    helper_elb = create_elb(hosted_zone_name='myhostedzone.gadevs.ga.')
    assert helper_elb.elb_r53


def test_elb_log_bucket():
    """
    Test elb log bucked is associated when when elb_log_bucket is supplied
    """
    helper_elb = create_elb(elb_log_bucket='my_elb_log_bucket')
    assert helper_elb.access_logging_policy
