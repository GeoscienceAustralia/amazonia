#!/usr/bin/python3

from nose.tools import *
from troposphere import Template, ec2, Ref

from amazonia.classes.subnet import Subnet

vpc = template = public_route_table = private_route_table = None
az = []
public_subnets = []
private_subnets = []


def setup_resources():
    """ Sets Up stack resources
    """
    global vpc, template, public_route_table, private_route_table, az, public_subnets, private_subnets
    template = Template()
    private_subnets = []
    public_subnets = []
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    public_route_table = template.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(vpc)))
    private_route_table = template.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                               VpcId=Ref(vpc)))
    az = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']

    # TODO change test referencing stack.pri_sub_list to pri_sub_list after tempalte refactor same with route tables


@with_setup(setup_resources)
def test_pub_or_pri():
    """ Validate that public/private subnet is correctly identified from route_table
    """

    for a in az:
        # For public subnets
        helper_pub_subnet = create_subnet(template=template, az=a, route_table=public_route_table, is_public=True)
        assert_equals(helper_pub_subnet.pub_or_pri, 'Public')

        # For private subnets
        helper_pri_subnet = create_subnet(template=template, az=a, route_table=private_route_table, is_public=False)
        assert_equals(helper_pri_subnet.pub_or_pri, 'Private')


@with_setup(setup_resources)
def test_add_associate_route_table():
    """ Validate route association created
    """
    for a in az:
        # For public subnets
        helper_pub_subnet = create_subnet(template=template, az=a, route_table=public_route_table, is_public=True)
        assert_true(helper_pub_subnet.rt_association)
        assert_equals(type(helper_pub_subnet.rt_association.RouteTableId), type(Ref(public_route_table)))
        assert_equals(type(helper_pub_subnet.rt_association.SubnetId), type(Ref(helper_pub_subnet)))
        assert_equals(helper_pub_subnet.rt_association.title,
                      public_route_table.title + helper_pub_subnet.trop_subnet.title + 'Association')

        # For private subnets
        helper_pri_subnet = create_subnet(template=template, az=a, route_table=private_route_table, is_public=False)
        assert_true(helper_pri_subnet.rt_association)
        assert_equals(type(helper_pri_subnet.rt_association.RouteTableId), type(Ref(private_route_table)))
        assert_equals(type(helper_pri_subnet.rt_association.SubnetId), type(Ref(helper_pri_subnet)))
        assert_equals(helper_pri_subnet.rt_association.title,
                      private_route_table.title + helper_pri_subnet.trop_subnet.title + 'Association')


def az_num(az_list):
    """ Helper function to validate number of subnets for a Single, Dual and Triple AZ senario passed in from test_az_num()
    """
    setup_resources()
    public_subnets_local = []
    private_subnets_local = []
    for a in az_list:
        public_subnets_local.append(
            create_subnet(template=template, az=a, route_table=public_route_table,
                          is_public=True))  # Append Public subnet
        private_subnets_local.append(
            create_subnet(template=template, az=a, route_table=private_route_table,
                          is_public=False))  # Append Private subnet
    assert_equals(len(az_list), len(public_subnets_local))
    assert_equals(len(az_list), len(private_subnets_local))


@with_setup(setup_resources)
def test_az_num():
    """ Validate number of subnets for a Single, Dual and Triple AZ senario passing to az_num(az_list) to validate length
    """
    my_az = list(az)
    while len(my_az) > 0:
        print(len(my_az))
        az_num(my_az)
        my_az.pop()


def create_subnet(**kwargs):
    """
    Helper function to create subnet objects.
    :return: Troposphere object for subnet,
    """
    third_octect = az.index(kwargs['az']) + 0 if kwargs['is_public'] else 100
    cidr = '10.0.{0}.0/24'.format(str(third_octect))
    subnet = Subnet(az=kwargs['az'],
                    template=template,
                    stack_title='MyStack',
                    route_table=kwargs['route_table'],
                    cidr=cidr,
                    is_public=kwargs['is_public'],
                    vpc=vpc)

    return subnet
