#!/usr/bin/python3

# noinspection PyUnresolvedReferences
import re

from amazonia.classes.elb import Elb
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.hosted_zone import HostedZone
from nose.tools import *
from troposphere import ec2, Ref, Template


def create_elb(instanceport='80', loadbalancerport='80', loadbalancer_protocol='HTTP', instance_protocol='HTTP',
               hosted_zone_name=None, elb_health_check='HTTP:80/index.html',
               elb_log_bucket=None, public_unit=True, ssl_certificate_id=None, healthy_threshold=10,
               unhealthy_threshold=2, interval=300, timeout=30):
    """
    Helper function to create Elb Troposhpere object to interate through.
    :param instanceport - port for traffic to instances from the load balancer
    :param loadbalancerport - port for traffic to the load balancer from public
    :param loadbalancer_protocol: protocol for traffic into ELB from World
    :param instance_protocol: protocol for traffic into ASG from ELB
    :param elb_health_check: path to test page
    :param elb_log_bucket: S3 bucket to log access log to
    :param hosted_zone_name: Route53 hosted zone ID
    :param public_unit: Boolean to determine if the elb scheme will be internet-facing or private
    :param ssl_certificate_id: SSL Certificate to attach to elb for https using AWS Certificate Manager
    :return: Troposphere object for Elb
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
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        is_nat=True,
        alert=None,
        alert_emails=None,
        public_hosted_zone_name=None,
        iam_instance_profile_arn=None
    )
    nat = SingleInstance(title='Nat',
                         template=template,
                         single_instance_config=single_instance_config)
    private_hosted_zone = HostedZone(vpcs=[vpc], template=template, domain='private.lan.')
    network_config = NetworkConfig(
        vpc=vpc,
        public_subnets=public_subnets,
        jump=None,
        nat=nat,
        private_subnets=private_subnets,
        public_cidr=None,
        public_hosted_zone_name=hosted_zone_name,
        private_hosted_zone=private_hosted_zone,
        cd_service_role_arn=None,
        keypair=None,
        nat_highly_available=False,
        nat_gateways=None
    )
    elb_config = ElbConfig(
        instance_port=[instanceport],
        loadbalancer_port=[loadbalancerport],
        loadbalancer_protocol=[loadbalancer_protocol],
        instance_protocol=[instance_protocol],
        elb_health_check=elb_health_check,
        elb_log_bucket=elb_log_bucket,
        public_unit=public_unit,
        ssl_certificate_id=ssl_certificate_id,
        healthy_threshold=healthy_threshold,
        unhealthy_threshold=unhealthy_threshold,
        interval=interval,
        timeout=timeout
    )

    elb = Elb(title='elb',
              template=Template(),
              network_config=network_config,
              elb_config=elb_config)
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
            helper_elb = create_elb(instance_protocol=protocol, loadbalancer_protocol=protocol)
            for listener in helper_elb.trop_elb.Listeners:
                assert_equal(protocol, listener.Protocol)
                assert_equal(protocol, listener.InstanceProtocol)

    helper_test_protocol(protocols)


def test_health_check_target():
    """
    Test to check that chealth check target inputs match the Target Address
    e.g. HTTP:80/index.html matches HTTP:80/index.html
    """
    elb_health_check_list = ['HTTP:80/index.html', 'HTTPS:443/index.html', 'HTTPS:443/index.html']

    def helper_test_protocol(elb_health_checks):
        for elb_health_check in elb_health_checks:
            helper_elb = create_elb(elb_health_check=elb_health_check)
            assert_equals(elb_health_check, helper_elb.trop_elb.HealthCheck.Target)

    helper_test_protocol(elb_health_check_list)


def test_target():
    """
    Tests to make sure that inputs of 'instance_protocol', 'loadbalancer_protocol', 'instanceport' and
    'elb_health_check' correctly forms target healthcheck url
    """
    helper_elb = create_elb(instance_protocol='HTTPS',
                            loadbalancer_protocol='HTTPS',
                            instanceport='443',
                            elb_health_check='HTTPS:443/test/index.html')
    assert_equals('HTTPS:443/test/index.html', helper_elb.trop_elb.HealthCheck.Target)


def test_instance_port():
    """
    Tests to validate that passing 'instanceport' correctly sets the instanceport in the Listener object of the ELB
    as well as the Health check target.
    'HealthCheck.Target', 'Listeners.InstancePort'
    """
    ports = ['8080', '80', '443', '5678', '-1', '99', '65535']

    for port in ports:
        helper_elb = create_elb(instanceport=port)
        for listener in helper_elb.trop_elb.Listeners:
            assert_equal(port, listener.InstancePort)


def test_loadbalancer_port():
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
    assert_true(helper_elb.elb_r53)


def test_no_hosted_zone_name():
    """
    Test that an elb is created without a route 53 record if none is supplied
    """
    helper_elb = create_elb()
    assert_false(helper_elb.elb_r53)


def test_elb_log_bucket():
    """
    Test elb log bucked is associated when when elb_log_bucket is supplied
    """
    helper_elb = create_elb(elb_log_bucket='my_elb_log_bucket')
    assert helper_elb.trop_elb.AccessLoggingPolicy


def test_public_unit():
    """
    Test to determine that elb scheme is private if public_unit is set to False
    """
    helper_elb = create_elb(public_unit=False)
    assert_equals(helper_elb.trop_elb.Scheme, 'internal')
    helper_elb = create_elb(public_unit=True)
    assert_equals(helper_elb.trop_elb.Scheme, 'internet-facing')


@AttributeError
def test_ssl_none():
    """
    # Test to determine that the ssl certificate is being passed into the elb listeners
    """
    helper_elb = create_elb(ssl_certificate_id=None)
    for listener in helper_elb.trop_elb.Listeners:
        assert_raises(listener.SSLCertificateId, AttributeError)


def test_ssl_certificate():
    """
    # Test to determine that the ssl certificate is being passed into the elb listeners
    """
    helper_elb = create_elb(ssl_certificate_id='arn:aws:acm::tester', loadbalancer_protocol='HTTPS')
    for listener in helper_elb.trop_elb.Listeners:
        assert_equals(listener.SSLCertificateId, 'arn:aws:acm::tester')


def test_thresholds():
    """
    Tests to validate that the healthy and unhealthy thresholds are being passed to the ELB HealthCheck
    """
    thresholds = [2, 10]

    for threshold in thresholds:
        helper_elb = create_elb(healthy_threshold=threshold)
        assert_equal(threshold, helper_elb.trop_elb.HealthCheck.HealthyThreshold)
        helper_elb = create_elb(unhealthy_threshold=threshold)
        assert_equal(threshold, helper_elb.trop_elb.HealthCheck.UnhealthyThreshold)


def test_interval():
    """
    Test to determine that elb scheme is private if public_unit is set to False
    """
    interval = 300
    timeout = 30

    helper_elb = create_elb(interval=interval, timeout=timeout)
    assert_equals(interval, helper_elb.trop_elb.HealthCheck.Interval)
    assert_equals(timeout, helper_elb.trop_elb.HealthCheck.Timeout)
