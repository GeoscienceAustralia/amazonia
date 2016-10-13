#!/usr/bin/python3

from amazonia.classes.network import Network
from troposphere import Ref, Output, Export


class Tree(Network):
    def __init__(self, tree_name, keypair, availability_zones, vpc_cidr, home_cidrs, public_cidr, jump_image_id,
                 jump_instance_type, nat_image_id, nat_instance_type, public_hosted_zone_name, private_hosted_zone_name,
                 iam_instance_profile_arn, owner_emails, nat_highly_available, ec2_scheduled_shutdown):
        """
        Create a vpc, nat, jumphost, internet gateway, public/private route tables, public/private subnets
         and collection of Amazonia units
        AWS CloudFormation -
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param tree_name: name of the tree used to created cross referenced stacks
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
        self.tree_name = tree_name

        super(Tree, self).__init__(keypair, availability_zones, vpc_cidr, home_cidrs, public_cidr, jump_image_id,
                                   jump_instance_type, nat_image_id, nat_instance_type, public_hosted_zone_name,
                                   private_hosted_zone_name,
                                   iam_instance_profile_arn, owner_emails, nat_highly_available, ec2_scheduled_shutdown)

        self.template.add_output(Output(
            'vpc',
            Description='VPC ID',
            Value=self.vpc,
            Export=Export(self.tree_name + '-VPC')
        ))

        self.template.add_output(Output(
            'jump',
            Description='Jump box Security group',
            Value=self.jump.security_group,
            Export=Export(self.tree_name + '-Jump')
        ))

        self.template.add_output(Output(
            'privateHostedZone',
            Description='Private Hosted Zone ID',
            Value=Ref(self.private_hosted_zone.trop_hosted_zone),
            Export=Export(self.tree_name + '-PrivateHostedZoneId')
        ))

        self.template.add_output(Output(
            'privateHostedZoneDomain',
            Description='Private Hosted Zone Domain',
            Value=self.private_hosted_zone.domain,
            Export=Export(self.tree_name + '-PrivateHostedZoneDomain')
        ))

        self.template.add_output(Output(
            'snsTopic',
            Description='Sns Topic',
            Value=Ref(self.sns_topic.trop_topic),
            Export=Export(self.tree_name + '-SnsTopic')
        ))

        for subnet in self.public_subnets:
            az = subnet.AvailabilityZone[-1:].upper()
            self.template.add_output(Output(
                'publicSubnet' + az,
                Description='Public Subnet ' + az,
                Value=Ref(subnet),
                Export=Export(self.tree_name + '-PublicSubnet-' + az)
            ))

        for subnet in self.private_subnets:
            az = subnet.AvailabilityZone[-1:].upper()
            self.template.add_output(Output(
                'privateSubnet' + az,
                Description='Private Subnet ' + az,
                Value=Ref(subnet),
                Export=Export(self.tree_name + '-PrivateSubnet-' + az)
            ))
