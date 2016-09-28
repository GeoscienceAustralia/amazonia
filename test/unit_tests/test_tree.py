from amazonia.classes.tree import Tree
from amazonia.classes.util import get_cf_friendly_name
from nose.tools import *
from troposphere import Tags, Ref

keypair = instance_type = vpc_cidr = public_cidr = nat_image_id = jump_image_id = owner_emails = None
availability_zones = []
home_cidrs = []


def setup_resources():
    global keypair, availability_zones, instance_type, vpc_cidr, public_cidr, home_cidrs, nat_image_id, jump_image_id, \
        owner_emails

    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    keypair = 'INSERT_YOUR_KEYPAIR_HERE'
    nat_image_id = 'ami-53371f30'
    jump_image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'
    vpc_cidr = {'name': 'VPC', 'cidr': '10.0.0.0/16'}
    home_cidrs = [{'name': 'GA', 'cidr': '123.123.12.34/32'}, {'name': 'home', 'cidr': '192.168.0.1/16'}]
    public_cidr = {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}
    owner_emails = ['some@email.com']


@with_setup(setup_resources)
def test_tree():
    """ Test stack structure
    """
    tee = create_tree()
    assert_equals(tee.keypair, keypair)
    assert_equals(tee.availability_zones, availability_zones)
    assert_equals(tee.vpc_cidr, vpc_cidr)
    [assert_equals(tee.home_cidrs[num], home_cidrs[num]) for num in range(len(home_cidrs))]
    assert_equals(tee.public_cidr, {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})

    assert_equals(tee.internet_gateway.title, 'Ig')
    assert_is(type(tee.internet_gateway.Tags), Tags)

    assert_equals(tee.gateway_attachment.title, 'IgAtch')
    assert_is(type(tee.gateway_attachment.VpcId), Ref)
    assert_is(type(tee.gateway_attachment.InternetGatewayId), Ref)

    assert_equals(tee.public_route_table.title, 'PubRouteTable')
    assert_is(type(tee.public_route_table.VpcId), Ref)
    assert_is(type(tee.public_route_table.Tags), Tags)

    for az in availability_zones:
        assert_equals(tee.private_route_tables[az].title, get_cf_friendly_name(az) + 'PriRouteTable')
        assert_is(type(tee.private_route_tables[az].VpcId), Ref)
        assert_is(type(tee.private_route_tables[az].Tags), Tags)

    assert_equals(tee.nat.single.SourceDestCheck, 'false')
    assert_equals(tee.jump.single.SourceDestCheck, 'true')

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = tee.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = tee.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))


@with_setup(setup_resources)
def test_highly_available_nat_tree():
    """ Test for nat gateway configuration"""

    tree = create_tree(nat_highly_available=True)

    assert_equals(tree.keypair, keypair)
    assert_equals(tree.availability_zones, availability_zones)
    assert_equals(tree.vpc_cidr, vpc_cidr)
    [assert_equals(tree.home_cidrs[num], home_cidrs[num]) for num in range(len(home_cidrs))]
    assert_equals(tree.public_cidr, {'name': 'PublicIp', 'cidr': '0.0.0.0/0'})

    assert_equals(tree.internet_gateway.title, 'Ig')
    assert_is(type(tree.internet_gateway.Tags), Tags)

    assert_equals(tree.gateway_attachment.title, 'IgAtch')
    assert_is(type(tree.gateway_attachment.VpcId), Ref)
    assert_is(type(tree.gateway_attachment.InternetGatewayId), Ref)

    assert_equals(tree.public_route_table.title, 'PubRouteTable')
    assert_is(type(tree.public_route_table.VpcId), Ref)
    assert_is(type(tree.public_route_table.Tags), Tags)

    for az in availability_zones:
        assert_equals(tree.private_route_tables[az].title, get_cf_friendly_name(az) + 'PriRouteTable')
        assert_is(type(tree.private_route_tables[az].VpcId), Ref)
        assert_is(type(tree.private_route_tables[az].Tags), Tags)

    assert_equals(len(tree.nat_gateways), len(availability_zones))
    assert_equals(tree.jump.single.SourceDestCheck, 'true')

    for num in range(len(availability_zones)):
        # For public subnets
        public_subnet = tree.public_subnets[num]
        assert_equals(public_subnet.CidrBlock, ''.join(['10.0.', str(num), '.0/24']))

        # For private subnets
        private_subnet = tree.private_subnets[num]
        assert_equals(private_subnet.CidrBlock, ''.join(['10.0.', str(num + 100), '.0/24']))


def create_tree(nat_highly_available=False):
    """
    Helper function to create a stack with default values
    :return new stack
    """

    return Tree(
        tree_name='testtree',
        keypair=keypair,
        availability_zones=availability_zones,
        vpc_cidr=vpc_cidr,
        public_cidr=public_cidr,
        home_cidrs=home_cidrs,
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        public_hosted_zone_name=None,
        private_hosted_zone_name='priavte.lan.',
        iam_instance_profile_arn=None,
        owner_emails=owner_emails,
        nat_highly_available=nat_highly_available,
    )
