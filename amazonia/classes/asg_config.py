class AsgConfig(object):
    def __init__(self, sns_topic_arn, sns_notification_types, cd_service_role_arn, health_check_grace_period,
                 health_check_type, keypair, minsize, maxsize, image_id, instance_type, userdata,
                 iam_instance_profile_arn, hdd_size=None):
        """
        Simple config class to contain autoscaling group related parameters
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        :param sns_topic_arn: ARN for sns topic to notify regarding autoscale events
        :param sns_notification_types: list of SNS autoscale notification types
        :param health_check_grace_period: The amount of time to wait for an instance to start before checking health
        :param health_check_type: The type of health check. currently 'ELB' or 'EC2' are the only valid types.
        :param hdd_size: the size of the hard drive on the instances.
        """
        self.sns_topic_arn = sns_topic_arn
        self.sns_notification_types = sns_notification_types
        self.cd_service_role_arn = cd_service_role_arn
        self.health_check_grace_period = health_check_grace_period
        self.health_check_type = health_check_type
        self.keypair = keypair
        self.minsize = minsize
        self.maxsize = maxsize
        self.image_id = image_id
        self.instance_type = instance_type
        self.userdata = userdata
        self.iam_instance_profile_arn = iam_instance_profile_arn
        self.hdd_size = hdd_size

    def define_undefined_values(self, other_asg_conifg):
        """
        Method to override undefined values with values from another ASGConfig class
        :param other_asg_conifg:
        """
        self.sns_topic_arn = other_asg_conifg.sns_topic_arn if self.sns_topic_arn is None else self.sns_topic_arn
        self.sns_notification_types = other_asg_conifg.sns_notification_types \
            if self.sns_notification_types is None else self.sns_notification_types
        self.cd_service_role_arn = other_asg_conifg.cd_service_role_arn \
            if self.cd_service_role_arn is None else self.cd_service_role_arn
        self.health_check_grace_period = other_asg_conifg.health_check_grace_period \
            if self.health_check_grace_period is None else self.health_check_grace_period
        self.health_check_type = other_asg_conifg.health_check_type \
            if self.health_check_type is None else self.health_check_type
        self.keypair = other_asg_conifg.keypair if self.keypair is None else self.keypair
        self.minsize = other_asg_conifg.minsize if self.minsize is None else self.minsize
        self.maxsize = other_asg_conifg.maxsize if self.maxsize is None else self.maxsize
        self.image_id = other_asg_conifg.image_id if self.image_id is None else self.image_id
        self.instance_type = other_asg_conifg.instance_type if self.instance_type is None else self.instance_type
        self.userdata = other_asg_conifg.userdata if self.userdata is None else self.userdata
        self.iam_instance_profile_arn = other_asg_conifg.iam_instance_profile_arn \
            if self.iam_instance_profile_arn is None else self.iam_instance_profile_arn
        self.hdd_size = other_asg_conifg.hdd_size if self.hdd_size is None else self.hdd_size
