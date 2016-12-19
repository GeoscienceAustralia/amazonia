#!/usr/bin/python3

from amazonia.classes.amz_api_gateway import ApiGatewayUnit
from amazonia.classes.amz_autoscaling import AutoscalingUnit
from amazonia.classes.amz_cf_distribution import CFDistributionUnit
from amazonia.classes.amz_database import DatabaseUnit
from amazonia.classes.amz_lambda import LambdaUnit
from amazonia.classes.network import Network
from amazonia.classes.stack_config import NetworkConfig
from amazonia.classes.amz_zd_autoscaling import ZdAutoscalingUnit
from troposphere import Ref


class Stack(Network):
    def __init__(self, code_deploy_service_role, keypair, availability_zones, vpc_cidr, home_cidrs,
                 public_cidr, jump_image_id, jump_instance_type, nat_image_id, nat_instance_type, zd_autoscaling_units,
                 autoscaling_units, database_units, cf_distribution_units, public_hosted_zone_name,
                 private_hosted_zone_name, iam_instance_profile_arn, owner_emails, api_gateway_units, lambda_units,
                 nat_highly_available, ec2_scheduled_shutdown, owner):
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
        :param ec2_scheduled_shutdown: True/False for whether to schedule shutdown for EC2 instances outside work hours
        """

        super(Stack, self).__init__(
            keypair, availability_zones, vpc_cidr, home_cidrs, public_cidr, jump_image_id,
            jump_instance_type, nat_image_id, nat_instance_type, public_hosted_zone_name,
            private_hosted_zone_name, iam_instance_profile_arn, owner_emails, nat_highly_available,
            ec2_scheduled_shutdown, owner)
        self.code_deploy_service_role = code_deploy_service_role
        self.autoscaling_units = autoscaling_units if autoscaling_units else []
        self.database_units = database_units if database_units else []
        self.cf_distribution_units = cf_distribution_units if cf_distribution_units else []
        self.zd_autoscaling_units = zd_autoscaling_units if zd_autoscaling_units else []
        self.api_gateway_units = api_gateway_units if api_gateway_units else []
        self.lambda_units = lambda_units if lambda_units else []
        self.units = {}
        self.network_config = None

        for autoscaling_unit in self.autoscaling_units:
            autoscaling_unit['ec2_scheduled_shutdown'] = ec2_scheduled_shutdown

        self.network_config = NetworkConfig(vpc=self.vpc,
                                            public_subnets=[Ref(subnet) for subnet in self.public_subnets],
                                            private_subnets=[Ref(subnet) for subnet in self.private_subnets],
                                            jump=self.jump,
                                            nat=self.nat,
                                            nat_highly_available=self.nat_highly_available,
                                            public_cidr=self.public_cidr,
                                            public_hosted_zone_name=self.public_hosted_zone_name,
                                            private_hosted_zone_id=Ref(self.private_hosted_zone.trop_hosted_zone),
                                            private_hosted_zone_domain=self.private_hosted_zone.domain,
                                            keypair=self.keypair,
                                            cd_service_role_arn=self.code_deploy_service_role,
                                            nat_gateways=self.nat_gateways,
                                            sns_topic=Ref(self.sns_topic.trop_topic),
                                            availability_zones=self.availability_zones)

        # Add Database Units
        self.add_units(self.database_units, DatabaseUnit)

        # Add ZD Autoscaling Units
        self.add_units(self.zd_autoscaling_units, ZdAutoscalingUnit)

        # Add Autoscaling Units
        self.add_units(self.autoscaling_units, AutoscalingUnit)

        # Add Lambda Units
        self.add_units(self.lambda_units, LambdaUnit)

        # Add ApiGateway Units
        self.add_units(self.api_gateway_units, ApiGatewayUnit)

        # Add Cloudfront Units
        self.add_units(self.cf_distribution_units, CFDistributionUnit)

    def add_units(self, unit_list, unit_constructor):
        for unit in unit_list:  # type: dict
            unit_title = unit['unit_title']
            if unit_title in self.units:
                raise DuplicateUnitNameError("Error: unit name '{0}' has already been specified, "
                                             'it must be unique.'.format(unit_title))
            self.units[unit_title] = unit_constructor(
                template=self.template,
                stack_config=self.network_config,
                **unit
            )


class DuplicateUnitNameError(Exception):
    def __init__(self, value):
        self.value = value
