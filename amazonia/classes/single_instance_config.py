#!/usr/bin/python3


class SingleInstanceConfig(object):
    def __init__(self, vpc, sns_topic, keypair, si_image_id, si_instance_type, subnet, availability_zone,
                 instance_dependencies, iam_instance_profile_arn, public_hosted_zone_name, is_nat,
                 ec2_scheduled_shutdown, owner):
        """
        Simple config class to contain networking related parameters
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param sns_topic: SNS topic to post alerts to
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param si_image_id: AWS ami id to create instance from, e.g. 'ami-12345'
        :param si_instance_type: Instance type for single instance e.g. 't2.micro' or 't2.nano'
        :param subnet: Troposhere object for subnet created e.g. 'sub_pub1'
        :param is_nat: a boolean that is used to determine if the instance will be a NAT or not. Default: False
        :param public_hosted_zone_name: A hosted zone name for setting up a Route 53 record set for Jump hosts
        :param instance_dependencies: a list of dependencies to wait for before creating the single instance.
        :param iam_instance_profile_arn: the ARN for an IAM profile that enables cloudwatch logging.
        :param availability_zone: availabiity zone to create single instance in
        :param ec2_scheduled_shutdown: True/False for whether to schedule shutdown for EC2 instances outside work hours
        :param owner: String value of owner tag
        """
        self.vpc = vpc
        self.sns_topic = sns_topic
        self.keypair = keypair
        self.si_image_id = si_image_id
        self.si_instance_type = si_instance_type
        self.subnet = subnet
        self.instance_dependencies = instance_dependencies
        self.iam_instance_profile_arn = iam_instance_profile_arn
        self.public_hosted_zone_name = public_hosted_zone_name
        self.is_nat = is_nat
        self.availability_zone = availability_zone
        self.ec2_scheduled_shutdown = ec2_scheduled_shutdown
        self.owner = owner
