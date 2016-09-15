#!/usr/bin/python3

from amazonia.classes.api_gateway_unit import ApiGatewayUnit
from amazonia.classes.autoscaling_unit import AutoscalingUnit
from amazonia.classes.cf_distribution_unit import CFDistributionUnit
from amazonia.classes.database_unit import DatabaseUnit
from amazonia.classes.hosted_zone import HostedZone
from amazonia.classes.lambda_unit import LambdaUnit
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.sns import SNS
from amazonia.classes.subnet import Subnet
from amazonia.classes.util import get_cf_friendly_name
from amazonia.classes.zd_autoscaling_unit import ZdAutoscalingUnit
from troposphere import Ref, Template, ec2, Tags, Join, GetAtt
from troposphere.ec2 import EIP, NatGateway


class Stack(object):
    def __init__(self, code_deploy_service_role, keypair, availability_zones, vpc_cidr, home_cidrs,
                 public_cidr, jump_image_id, jump_instance_type, nat_image_id, nat_instance_type, zd_autoscaling_units,
                 autoscaling_units, database_units, cf_distribution_units, public_hosted_zone_name,
                 private_hosted_zone_name, iam_instance_profile_arn, owner_emails, api_gateway_units, lambda_units,
                 nat_highly_available):
        """
        Create a vpc, nat, jumphost, internet gateway, public/private route tables, public/private subnets
         and collection of Amazonia units
        AWS CloudFormation -
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param code_deploy_service_role: ARN to code deploy IAM role
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
        :param zd_autoscaling_units: list of zd_autosclaing_unit dicts
        :param autoscaling_units: list of autoscaling_unit dicts (unit_title, protocol, port, elb_health_check, minsize,
        maxsize, image_id, instance_type, userdata)
        :param database_units: list of database_unit dicts (db_instance_type, db_engine, db_port)
        :param cf_distribution_units: list of cf_distribution_unit dicts
        :param api_gateway_units: list of api_gateway_unit dicts
        :param lambda_units: List of lambda_unit dicts
        :param public_hosted_zone_name: A string containing the name of the Route 53 hosted zone to create public record
        sets in.
        :param private_hosted_zone_name: name of private hosted zone to create
        :param iam_instance_profile_arn: the ARN for an IAM instance profile that enables cloudtrail access for logging
        :param owner_emails: a list of emails for owners of this stack. Used for alerting.
        :param nat_highly_available: True/False for whether or not to use a series of NAT gateways or a single NAT
        """

        super(Stack, self).__init__()
        # set parameters
        self.code_deploy_service_role = code_deploy_service_role
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
        self.owner_emails = owner_emails
        self.nat_highly_available = nat_highly_available
        self.autoscaling_units = autoscaling_units if autoscaling_units else []
        self.database_units = database_units if database_units else []
        self.cf_distribution_units = cf_distribution_units if cf_distribution_units else []
        self.zd_autoscaling_units = zd_autoscaling_units if zd_autoscaling_units else []
        self.api_gateway_units = api_gateway_units if api_gateway_units else []
        self.lambda_units = lambda_units if lambda_units else []
        self.iam_instance_profile_arn = iam_instance_profile_arn

        # initialize object references
        self.template = Template()
        self.units = {}
        self.private_subnets = []
        self.public_subnets = []
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
        self.network_config = None
        self.sns_topic = None

        self.setup_vpc()

        # Add ZD Autoscaling Units
        self.add_units(self.zd_autoscaling_units, ZdAutoscalingUnit)

        # Add Autoscaling Units
        self.add_units(self.autoscaling_units, AutoscalingUnit)

        # Add Database Units
        self.add_units(self.database_units, DatabaseUnit)

        # Add Cloudfront Units
        self.add_units(self.cf_distribution_units, CFDistributionUnit)

        # Add ApiGateway Units
        self.add_units(self.api_gateway_units, ApiGatewayUnit)

        # Add Lambda Units
        self.add_units(self.lambda_units, LambdaUnit)

        # Add Unit flow
        for unit_name in self.units:
            dependencies = self.units[unit_name].get_dependencies()
            for dependency in dependencies:
                self.units[unit_name].add_unit_flow(self.units[dependency])

    def setup_vpc(self):
        # Add VPC and Internet Gateway with Attachment
        vpc_name = 'Vpc'
        self.vpc = self.template.add_resource(
            ec2.VPC(
                vpc_name,
                CidrBlock=self.vpc_cidr,
                EnableDnsSupport='true',
                EnableDnsHostnames='true',
                Tags=Tags(
                    Name=Join('', [Ref('AWS::StackName'), '-', vpc_name])
                )
            ))
        self.private_hosted_zone = HostedZone(self.template, self.private_hosted_zone_name, vpcs=[self.vpc])
        ig_name = 'Ig'
        self.internet_gateway = self.template.add_resource(
            ec2.InternetGateway(ig_name,
                                Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', ig_name])),
                                DependsOn=self.vpc.title))

        self.gateway_attachment = self.template.add_resource(
            ec2.VPCGatewayAttachment(self.internet_gateway.title + 'Atch',
                                     VpcId=Ref(self.vpc),
                                     InternetGatewayId=Ref(self.internet_gateway),
                                     DependsOn=self.internet_gateway.title))

        # Add Public Route Table
        public_rt_name = 'PubRouteTable'
        self.public_route_table = self.template.add_resource(
            ec2.RouteTable(public_rt_name, VpcId=Ref(self.vpc),
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', public_rt_name]))))

        # Add Public and Private Subnets and Private Route Table
        for az in self.availability_zones:
            private_rt_name = get_cf_friendly_name(az) + 'PriRouteTable'
            private_route_table = self.template.add_resource(
                ec2.RouteTable(private_rt_name, VpcId=Ref(self.vpc),
                               Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', private_rt_name]))))
            self.private_route_tables[az] = private_route_table

            self.private_subnets.append(Subnet(template=self.template,
                                               route_table=private_route_table,
                                               az=az,
                                               vpc=self.vpc,
                                               is_public=False,
                                               cidr=self.generate_subnet_cidr(is_public=False)).trop_subnet)
            self.public_subnets.append(Subnet(template=self.template,
                                              route_table=self.public_route_table,
                                              az=az,
                                              vpc=self.vpc,
                                              is_public=True,
                                              cidr=self.generate_subnet_cidr(is_public=True)).trop_subnet)

        self.sns_topic = SNS(self.template)

        for email in self.owner_emails:
            self.sns_topic.add_subscription(email, 'email')

        jump_config = SingleInstanceConfig(
            keypair=self.keypair,
            si_image_id=self.jump_image_id,
            si_instance_type=self.jump_instance_type,
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            public_hosted_zone_name=self.public_hosted_zone_name,
            instance_dependencies=self.gateway_attachment.title,
            iam_instance_profile_arn=self.iam_instance_profile_arn,
            is_nat=False,
            sns_topic=self.sns_topic
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
                subnet=self.public_subnets[0],
                vpc=self.vpc,
                is_nat=True,
                instance_dependencies=self.gateway_attachment.title,
                iam_instance_profile_arn=self.iam_instance_profile_arn,
                public_hosted_zone_name=None,
                sns_topic=self.sns_topic
            )

            self.nat = SingleInstance(
                title='Nat',
                template=self.template,
                single_instance_config=nat_config
            )
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

        self.network_config = NetworkConfig(vpc=self.vpc,
                                            public_subnets=self.public_subnets,
                                            private_subnets=self.private_subnets,
                                            jump=self.jump,
                                            nat=self.nat,
                                            nat_highly_available=self.nat_highly_available,
                                            public_cidr=self.public_cidr,
                                            public_hosted_zone_name=self.public_hosted_zone_name,
                                            private_hosted_zone=self.private_hosted_zone,
                                            keypair=self.keypair,
                                            cd_service_role_arn=self.code_deploy_service_role,
                                            nat_gateways=self.nat_gateways,
                                            sns_topic=self.sns_topic)

    def add_units(self, unit_list, unit_constructor):
        for unit in unit_list:  # type: dict
            unit_title = unit['unit_title']
            if unit_title in self.units:
                raise DuplicateUnitNameError("Error: unit name '{0}' has already been specified, "
                                             'it must be unique.'.format(unit_title))
            self.units[unit_title] = unit_constructor(
                template=self.template,
                network_config=self.network_config,
                **unit
            )

    def generate_subnet_cidr(self, is_public):
        """
        Function to help create Class C subnet CIDRs from Class A VPC CIDRs
        :param is_public: boolean for public or private subnet determined by route table
        :return: Subnet CIDR based on Public or Private and previous subnets created e.g. 10.0.2.0/24 or 10.0.101.0/24
        """
        # 3rd Octet: Obtain length of pub or pri subnet list
        octet_3 = len(self.public_subnets) if is_public else len(self.private_subnets) + 100
        cidr_split = self.vpc.CidrBlock.split('.')  # separate VPC CIDR for renaming
        cidr_split[2] = str(octet_3)  # set 3rd octet based on public or private
        cidr_last = cidr_split[3].split('/')  # split last group to change subnet mask
        cidr_last[1] = '24'  # set subnet mask
        cidr_split[3] = '/'.join(cidr_last)  # join last group for subnet mask

        return '.'.join(cidr_split)


class DuplicateUnitNameError(Exception):
    def __init__(self, value):
        self.value = value
