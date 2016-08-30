#!/usr/bin/python3

from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.autoscaling_unit import AutoscalingUnit
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.database_unit import DatabaseUnit
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.subnet import Subnet
from amazonia.classes.zd_autoscaling_unit import ZdAutoscalingUnit

from troposphere import Ref, Template, ec2, Tags, Join


class Stack(object):
    def __init__(self, stack_title, code_deploy_service_role, keypair, availability_zones, vpc_cidr, home_cidrs,
                 public_cidr, jump_image_id, jump_instance_type, nat_image_id, nat_instance_type, zd_autoscaling_units,
                 autoscaling_units, database_units, stack_hosted_zone_name, iam_instance_profile_arn, owner_emails,
                 nat_alerting):
        """
        Create a vpc, nat, jumphost, internet gateway, public/private route tables, public/private subnets
         and collection of Amazonia units
        AWS CloudFormation -
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param stack_title: name of stack
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
        :param database_units: list of dabase_unit dicts (db_instance_type, db_engine, db_port)
        :param stack_hosted_zone_name: A string containing the name of the Route 53 hosted zone to create record
        sets in.
        :param iam_instance_profile_arn: the ARN for an IAM instance profile that enables cloudtrail access for logging
        :param owner_emails: a list of emails for owners of this stack. Used for alerting.
        :param nat_alerting: True/False for whether or not to alert on the nat instance status.
        """

        super(Stack, self).__init__()
        self.title = stack_title
        self.template = Template()
        self.code_deploy_service_role = code_deploy_service_role
        self.keypair = keypair
        self.availability_zones = availability_zones
        self.vpc_cidr = vpc_cidr
        self.home_cidrs = home_cidrs
        self.public_cidr = public_cidr
        self.hosted_zone_name = stack_hosted_zone_name
        self.autoscaling_units = autoscaling_units if autoscaling_units else []
        self.database_units = database_units if database_units else []
        self.zd_autoscaling_units = zd_autoscaling_units if zd_autoscaling_units else []
        self.iam_instance_profile_arn = iam_instance_profile_arn
        self.units = {}
        self.private_subnets = []
        self.public_subnets = []

        # Add VPC and Internet Gateway with Attachment
        vpc_name = self.title + 'Vpc'
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

        ig_name = self.title + 'Ig'
        self.internet_gateway = self.template.add_resource(
            ec2.InternetGateway(ig_name,
                                Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', ig_name])),
                                DependsOn=self.vpc.title))

        self.gateway_attachment = self.template.add_resource(
            ec2.VPCGatewayAttachment(self.internet_gateway.title + 'Atch',
                                     VpcId=Ref(self.vpc),
                                     InternetGatewayId=Ref(self.internet_gateway),
                                     DependsOn=self.internet_gateway.title))

        # Add Public and Private Route Tables
        public_rt_name = self.title + 'PubRt'
        self.public_route_table = self.template.add_resource(
            ec2.RouteTable(public_rt_name, VpcId=Ref(self.vpc),
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', public_rt_name]))))

        private_rt_name = self.title + 'PriRt'
        self.private_route_table = self.template.add_resource(
            ec2.RouteTable(private_rt_name, VpcId=Ref(self.vpc),
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', private_rt_name]))))

        # Add Public and Private Subnets
        for az in self.availability_zones:
            self.private_subnets.append(Subnet(template=self.template,
                                               stack_title=self.title,
                                               route_table=self.private_route_table,
                                               az=az,
                                               vpc=self.vpc,
                                               is_public=False,
                                               cidr=self.generate_subnet_cidr(is_public=False)).trop_subnet)
            self.public_subnets.append(Subnet(template=self.template,
                                              stack_title=self.title,
                                              route_table=self.public_route_table,
                                              az=az,
                                              vpc=self.vpc,
                                              is_public=True,
                                              cidr=self.generate_subnet_cidr(is_public=True)
                                              ).trop_subnet)

        jump_config = SingleInstanceConfig(
            keypair=self.keypair,
            si_image_id=jump_image_id,
            si_instance_type=jump_instance_type,
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            hosted_zone_name=self.hosted_zone_name,
            instance_dependencies=self.gateway_attachment.title,
            iam_instance_profile_arn=self.iam_instance_profile_arn,
            alert_emails=owner_emails,
            alert=nat_alerting,
            is_nat=False
        )

        # Add Jumpbox and NAT and associated security group ingress and egress rules
        self.jump = SingleInstance(
            title=self.title + 'Jump',
            template=self.template,
            single_instance_config=jump_config
        )

        [self.jump.add_ingress(sender=home_cidr, port='22') for home_cidr in self.home_cidrs]
        self.jump.add_egress(receiver=self.public_cidr, port='-1')

        nat_config = SingleInstanceConfig(
            keypair=self.keypair,
            si_image_id=nat_image_id,
            si_instance_type=nat_instance_type,
            subnet=self.public_subnets[0],
            vpc=self.vpc,
            is_nat=True,
            instance_dependencies=self.gateway_attachment.title,
            iam_instance_profile_arn=self.iam_instance_profile_arn,
            alert_emails=owner_emails,
            alert=nat_alerting,
            hosted_zone_name=None
        )

        self.nat = SingleInstance(
            title=self.title + 'Nat',
            template=self.template,
            single_instance_config=nat_config
        )

        # Add Routes
        self.public_route = self.template.add_resource(ec2.Route(self.title + 'PubRtInboundRoute',
                                                                 GatewayId=Ref(self.internet_gateway),
                                                                 RouteTableId=Ref(self.public_route_table),
                                                                 DestinationCidrBlock=self.public_cidr['cidr'],
                                                                 DependsOn=self.gateway_attachment.title))

        self.private_route = self.template.add_resource(ec2.Route(self.title + 'PriRtOutboundRoute',
                                                                  InstanceId=Ref(self.nat.single),
                                                                  RouteTableId=Ref(self.private_route_table),
                                                                  DestinationCidrBlock=self.public_cidr['cidr'],
                                                                  DependsOn=self.gateway_attachment.title))

        self.network_config = NetworkConfig(vpc=self.vpc,
                                            public_subnets=self.public_subnets,
                                            private_subnets=self.private_subnets,
                                            jump=self.jump,
                                            nat=self.nat,
                                            public_cidr=self.public_cidr,
                                            stack_hosted_zone_name=self.hosted_zone_name,
                                            keypair=self.keypair,
                                            cd_service_role_arn=self.code_deploy_service_role
                                            )
        # Add ZD Autoscaling Units
        for unit in self.zd_autoscaling_units:  # type: dict
            orig_unit_title = unit['unit_title']
            if orig_unit_title in self.units:
                raise DuplicateUnitNameError("Error: zd_autoscaling unit name '{0}' has already been specified, "
                                             'it must be unique.'.format(orig_unit_title))
            # Update unit title with stackname prefix
            unit['unit_title'] = self.title + orig_unit_title
            elb_config = ElbConfig(**unit['elb_config'])

            blue_asg_config = AsgConfig(**unit['blue_asg_config'])
            green_asg_config = AsgConfig(**unit['green_asg_config'])
            self.units[orig_unit_title] = ZdAutoscalingUnit(
                unit_title=unit['unit_title'],
                template=self.template,
                network_config=self.network_config,
                elb_config=elb_config,
                blue_asg_config=blue_asg_config,
                green_asg_config=green_asg_config,
                dependencies=unit['dependencies']
            )
        # Add Autoscaling Units
        for unit in self.autoscaling_units:  # type: dict
            orig_unit_title = unit['unit_title']
            if orig_unit_title in self.units:
                raise DuplicateUnitNameError("Error: autoscaling unit name '{0}' has already been specified, "
                                             'it must be unique.'.format(orig_unit_title))
            # Update unit title with stackname prefix
            unit['unit_title'] = self.title + orig_unit_title
            elb_config = ElbConfig(**unit['elb_config'])
            asg_config = AsgConfig(**unit['asg_config'])
            self.units[orig_unit_title] = AutoscalingUnit(
                unit_title=unit['unit_title'],
                template=self.template,
                network_config=self.network_config,
                elb_config=elb_config,
                asg_config=asg_config,
                dependencies=unit['dependencies']
            )
        # Add Database Units
        for unit in self.database_units:  # type: dict
            orig_unit_title = unit['unit_title']
            if orig_unit_title in self.units:
                raise DuplicateUnitNameError("Error: database unit name '{0}' has already been specified, "
                                             'it must be unique.'.format(orig_unit_title))
            unit['unit_title'] = self.title + orig_unit_title
            database_config = DatabaseConfig(**unit['database_config'])
            self.units[orig_unit_title] = DatabaseUnit(
                unit_title=unit['unit_title'],
                template=self.template,
                network_config=self.network_config,
                database_config=database_config
            )
        # Add Unit flow
        for unit_name in self.units:
            dependencies = self.units[unit_name].get_dependencies()
            for dependency in dependencies:
                self.units[unit_name].add_unit_flow(self.units[dependency])

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
