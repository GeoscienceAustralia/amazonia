#!/usr/bin/python3

from amazonia.classes.subnet import Subnet
from troposphere import ec2, Ref, Template


def main():
    template = Template()
    az_a = 'ap-southeast-2a'
    az_b = 'ap-southeast-2b'
    az_c = 'ap-southeast-2c'

    private_subnets = []
    public_subnets = []

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    public_route_table = template.add_resource(ec2.RouteTable('MyUnitPublicRouteTable',
                                                              VpcId=Ref(vpc)))
    private_route_table = template.add_resource(ec2.RouteTable('MyUnitPrivateRouteTable',
                                                               VpcId=Ref(vpc)))

    public_subnets.append(Subnet(template=template,
                                 route_table=public_route_table,
                                 az=az_a,
                                 cidr='10.0.1.0/24',
                                 vpc=vpc,
                                 is_public=True,
                                 stack_title='MyStack'))
    public_subnets.append(Subnet(template=template,
                                 route_table=public_route_table,
                                 az=az_b,
                                 cidr='10.0.2.0/24',
                                 vpc=vpc,
                                 is_public=True,
                                 stack_title='MyStack'))
    public_subnets.append(Subnet(template=template,
                                 route_table=public_route_table,
                                 az=az_c,
                                 cidr='10.0.3.0/24',
                                 vpc=vpc,
                                 is_public=True,
                                 stack_title='MyStack'))
    private_subnets.append(Subnet(template=template,
                                  route_table=private_route_table,
                                  az=az_a,
                                  cidr='10.0.101.0/24',
                                  vpc=vpc,
                                  is_public=False,
                                  stack_title='MyStack'))
    private_subnets.append(Subnet(template=template,
                                  route_table=private_route_table,
                                  az=az_b,
                                  cidr='10.0.102.0/24',
                                  vpc=vpc,
                                  is_public=False,
                                  stack_title='MyStack'))
    private_subnets.append(Subnet(template=template,
                                  route_table=private_route_table,
                                  az=az_c,
                                  cidr='10.0.103.0/24',
                                  vpc=vpc,
                                  is_public=False,
                                  stack_title='MyStack'))

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == "__main__":
    main()
