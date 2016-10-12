#!/usr/bin/python3

from amazonia.classes.hosted_zone import HostedZone
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.sns import SNS
from amazonia.classes.subnet import Subnet
from amazonia.classes.util import get_cf_friendly_name
from troposphere import Ref, Template, ec2, Tags, Join, GetAtt
from troposphere.ec2 import EIP, NatGateway


class Network(object):
    def __init__(self, keypair, availability_zones, vpc_cidr, home_cidrs, public_cidr, jump_image_id,
                 jump_instance_type, nat_image_id, nat_instance_type, public_hosted_zone_name, private_hosted_zone_name,
                 iam_instance_profile_arn, owner_emails, nat_highly_available, ec2_scheduled_shutdown):
        """
        Create a vpc, nat, jumphost, internet gateway, public/private route tables, public/private subnets
         and collection of Amazonia units
        AWS CloudFormation -
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param keypair: ssh keypair to be used throughout stack
        :param availability_zones: availability zones to use
        :param vpc_cidr: cidr pattern for vpc
        :param home_cidrs: a list of tuple objects of 'title'(0) and 'ip'(1) to be used
         to create ingress rules for ssh to jumpboxes from home/office/company premises
        :param public_cidr: a cidr to be treated as a public location. (eg 0.0.0.0/0)
        :param jump_image_id: AMI for jumphost
        :param jump_instance_type: instance type for jumphost
        :param nat_image_id: AMI for nat
        :param nat_instance_type: instance type for nat
        :param public_hosted_zone_name: A string containing the name of the Route 53 hosted zone to create public record
        sets in.
        :param private_hosted_zone_name: name of private hosted zone to create
        :param iam_instance_profile_arn: the ARN for an IAM instance profile that enables cloudtrail access for logging
        :param owner_emails: a list of emails for owners of this stack. Used for alerting.
        :param nat_highly_available: True/False for whether or not to use a series of NAT gateways or a single NAT
        :param ec2_scheduled_shutdown: True/False for whether to schedule shutdown for EC2 instances outside work hours
        """

        super(Network, self).__init__()
        # set parameters
        self.keypair = keypair
        self.availability_zones = availability_zones
        self.vpc_cidr = vpc_cidr
        self.home_cidrs = home_cidrs
        self.public_cidr = public_cidr
        self.public_hosted_zone_name = public_hosted_zone_name
        self.private_hosted_zone_name = private_hosted_zone_name
        self.jump_image_id = jump_image_id
        self.jump_instance_type = jump_instance_type
        self.nat_image_id = nat_image_id
        self.nat_instance_type = nat_instance_type
        self.owner_emails = owner_emails if owner_emails else []
        self.nat_highly_available = nat_highly_available
        self.iam_instance_profile_arn = iam_instance_profile_arn
        self.ec2_scheduled_shutdown = ec2_scheduled_shutdown

        # initialize object references
        self.template = Template()
        self.private_subnets = []
        self.public_subnets = []
        self.public_subnet_mapping = {}
        self.vpc = None
        self.private_hosted_zone = None
        self.internet_gateway = None
        self.gateway_attachment = None
        self.public_route_table = None
        self.private_route_tables = {}
        self.nat = None
        self.nat_gateways = []
        self.jump = None
        self.private_route = None
        self.public_route = None
        self.sns_topic = None

        # Add VPC and Internet Gateway with Attachment
        vpc_name = 'Vpc'
        self.vpc = Ref(self.template.add_resource(
            ec2.VPC(
                vpc_name,
                CidrBlock=self.vpc_cidr['cidr'],
                EnableDnsSupport='true',
                EnableDnsHostnames='true',
                Tags=Tags(
                    Name=Join('', [Ref('AWS::StackName'), '-', vpc_name])
                )
            )))
        self.private_hosted_zone = HostedZone(self.template, self.private_hosted_zone_name, vpcs=[self.vpc])
        ig_name = 'Ig'
        self.internet_gateway = self.template.add_resource(
            ec2.InternetGateway(ig_name,
                                Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', ig_name])),
                                DependsOn=vpc_name))

        self.gateway_attachment = self.template.add_resource(
            ec2.VPCGatewayAttachment(self.internet_gateway.title + 'Atch',
                                     VpcId=self.vpc,
                                     InternetGatewayId=Ref(self.internet_gateway),
                                     DependsOn=self.internet_gateway.title))

        # Add Public Route Table
        public_rt_name = 'PubRouteTable'
        self.public_route_table = self.template.add_resource(
            ec2.RouteTable(public_rt_name, VpcId=self.vpc,
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', public_rt_name]))))

        # Add Public and Private Subnets and Private Route Table
        for az in self.availability_zones:
            private_rt_name = get_cf_friendly_name(az) + 'PriRouteTable'
            private_route_table = self.template.add_resource(
                ec2.RouteTable(private_rt_name, VpcId=self.vpc,
                               Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', private_rt_name]))))
            self.private_route_tables[az] = private_route_table

            self.private_subnets.append(Subnet(template=self.template,
                                               route_table=private_route_table,
                                               az=az,
                                               vpc=self.vpc,
                                               is_public=False,
                                               cidr=self.generate_subnet_cidr(is_public=False)).trop_subnet)
            public_subnet = Subnet(template=self.template,
                                   route_table=self.public_route_table,
                                   az=az,
                                   vpc=self.vpc,
                                   is_public=True,
                                   cidr=self.generate_subnet_cidr(is_public=True)).trop_subnet
            self.public_subnets.append(public_subnet)
            self.public_subnet_mapping[az] = Ref(public_subnet)

        self.sns_topic = SNS(self.template)

        for email in self.owner_emails:
            self.sns_topic.add_subscription(email, 'email')

        jump_config = SingleInstanceConfig(
            keypair=self.keypair,
            si_image_id=self.jump_image_id,
            si_instance_type=self.jump_instance_type,
            subnet=self.public_subnet_mapping[availability_zones[0]],
            vpc=self.vpc,
            public_hosted_zone_name=self.public_hosted_zone_name,
            instance_dependencies=self.gateway_attachment.title,
            iam_instance_profile_arn=self.iam_instance_profile_arn,
            is_nat=False,
            sns_topic=self.sns_topic,
            availability_zone=availability_zones[0],
            ec2_scheduled_shutdown=self.ec2_scheduled_shutdown
        )

        # Add Jumpbox and NAT and associated security group ingress and egress rules
        self.jump = SingleInstance(
            title='Jump',
            template=self.template,
            single_instance_config=jump_config
        )

        [self.jump.add_ingress(sender=home_cidr, port='22') for home_cidr in self.home_cidrs]
        self.jump.add_egress(receiver=self.public_cidr, port='-1')

        if self.nat_highly_available:
            for public_subnet in self.public_subnets:
                az = public_subnet.AvailabilityZone
                ip_address = self.template.add_resource(
                    EIP(get_cf_friendly_name(az) + 'NatGwEip',
                        DependsOn=self.gateway_attachment.title,
                        Domain='vpc'
                        ))

                nat_gateway = self.template.add_resource(NatGateway(get_cf_friendly_name(az) + 'NatGw',
                                                                    AllocationId=GetAtt(ip_address, 'AllocationId'),
                                                                    SubnetId=Ref(public_subnet),
                                                                    DependsOn=self.gateway_attachment.title
                                                                    ))
                self.nat_gateways.append(nat_gateway)

                self.template.add_resource(ec2.Route(get_cf_friendly_name(az) + 'PriRoute',
                                                     NatGatewayId=Ref(nat_gateway),
                                                     RouteTableId=Ref(self.private_route_tables[az]),
                                                     DestinationCidrBlock=self.public_cidr['cidr'],
                                                     DependsOn=self.gateway_attachment.title))

        else:
            nat_config = SingleInstanceConfig(
                keypair=self.keypair,
                si_image_id=self.nat_image_id,
                si_instance_type=self.nat_instance_type,
                subnet=self.public_subnet_mapping[availability_zones[0]],
                vpc=self.vpc,
                is_nat=True,
                instance_dependencies=self.gateway_attachment.title,
                iam_instance_profile_arn=self.iam_instance_profile_arn,
                public_hosted_zone_name=None,
                sns_topic=self.sns_topic,
                availability_zone=availability_zones[0],
                ec2_scheduled_shutdown=self.ec2_scheduled_shutdown
            )

            self.nat = SingleInstance(
                title='Nat',
                template=self.template,
                single_instance_config=nat_config
            )

            self.nat.add_egress(receiver=self.public_cidr, port='-1')
            self.nat.add_ingress(sender=self.vpc_cidr, port='-1')
            for az in self.availability_zones:
                self.template.add_resource(ec2.Route(get_cf_friendly_name(az) + 'PriRoute',
                                                     InstanceId=Ref(self.nat.single),
                                                     RouteTableId=Ref(self.private_route_tables[az]),
                                                     DestinationCidrBlock=self.public_cidr['cidr'],
                                                     DependsOn=self.gateway_attachment.title))
        # Add Public Route
        self.public_route = self.template.add_resource(ec2.Route('PubRoute',
                                                                 GatewayId=Ref(self.internet_gateway),
                                                                 RouteTableId=Ref(self.public_route_table),
                                                                 DestinationCidrBlock=self.public_cidr['cidr'],
                                                                 DependsOn=self.gateway_attachment.title))

    def generate_subnet_cidr(self, is_public):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param is_public: boolean for public or private subnet determined by route table
        :return: Subnet CIDR based on Public or Private and previous subnets created e.g. 10.0.2.0/24 or 10.0.101.0/24
        """
        # 3rd Octet: Obtain length of pub or pri subnet list
        octet_3 = len(self.public_subnets) if is_public else len(self.private_subnets) + 100
        cidr_split = self.vpc_cidr['cidr'].split('.')  # separate VPC CIDR for renaming
        cidr_split[2] = str(octet_3)  # set 3rd octet based on public or private
        cidr_last = cidr_split[3].split('/')  # split last group to change subnet mask
        cidr_last[1] = '24'  # set subnet mask
        cidr_split[3] = '/'.join(cidr_last)  # join last group for subnet mask

        return '.'.join(cidr_split)
