#!/usr/bin/python3
from troposphere import ec2, Tags, Ref, Join


class Subnet(object):
    def __init__(self, template, stack_title, cidr, vpc, route_table, is_public, az):
        """
        Class to create subnets and associate a route table to it
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param template: Troposhere template object
        :param stack_title: Stack title from stack class
        :param cidr: cidr for subnet
        :param vpc: VPC to create subnet in
        :param route_table: Public or private route table object from stack
        :param is_public: boolean inidicating if subnet is public or not
        :param az: Availability zone where the subnet will be deployed
        """
        super(Subnet, self).__init__()

        self.template = template
        self.cidr = cidr
        self.vpc = vpc
        self.stack_title = stack_title
        self.pub_or_pri = 'Public' if is_public else 'Private'

        """ Create Subnet
        """
        subnet_title = self.stack_title + self.pub_or_pri + 'Subnet' + az[-1:].upper()
        self.trop_subnet = self.template.add_resource(ec2.Subnet(subnet_title,
                                                                 AvailabilityZone=az,
                                                                 VpcId=Ref(self.vpc),
                                                                 CidrBlock=self.cidr,
                                                                 Tags=Tags(Name=Join("",
                                                                                     [Ref('AWS::StackName'),
                                                                                      '-',
                                                                                      subnet_title]))))

        """ Create Route Table Associations
        """
        self.rt_association = self.create_associate_route_table(route_table)

    def create_associate_route_table(self, route_table):
        """
        Function to create a route table association
        AWS CloudFormation -
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet-route-table-assoc.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param route_table: Public or private route table object from stack
        """

        route_table_assoc = self.template.add_resource(ec2.SubnetRouteTableAssociation(route_table.title +
                                                                                       self.trop_subnet.title +
                                                                                       'Association',
                                                                                       RouteTableId=Ref(route_table),
                                                                                       SubnetId=Ref(self.trop_subnet)))
        return route_table_assoc
