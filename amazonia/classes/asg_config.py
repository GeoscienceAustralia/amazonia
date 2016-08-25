#!/usr/bin/python3

from amazonia.classes.util import detect_unencrypted_access_keys


class InvalidAsgConfigError(Exception):
    def __init__(self, value):
        self.value = value


class AsgConfig(object):
    def __init__(self, sns_topic_arn, sns_notification_types, health_check_grace_period,
                 health_check_type, minsize, maxsize, image_id, instance_type, userdata,
                 iam_instance_profile_arn, block_devices_config, simple_scaling_policy_config):
        """
        Simple config class to contain autoscaling group related parameters
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param sns_topic_arn: ARN for sns topic to notify regarding autoscale events
        :param sns_notification_types: list of SNS autoscale notification types
        :param health_check_grace_period: The amount of time to wait for an instance to start before checking health
        :param health_check_type: The type of health check. currently 'ELB' or 'EC2' are the only valid types.
        :param block_devices_config: List containing block device mappings
        :param simple_scaling_policy_config: List containing scaling policies
        """
        self.sns_topic_arn = sns_topic_arn
        self.sns_notification_types = sns_notification_types
        self.health_check_grace_period = health_check_grace_period
        self.health_check_type = health_check_type
        self.minsize = minsize
        self.maxsize = maxsize
        self.image_id = image_id
        self.instance_type = instance_type
        self.userdata = userdata
        self.iam_instance_profile_arn = iam_instance_profile_arn
        self.block_devices_config = block_devices_config
        self.simple_scaling_policy_config = simple_scaling_policy_config

        # check for insecure variables
        detect_unencrypted_access_keys(self.userdata)

        # Validate that minsize is less than maxsize
        if self.minsize > self.maxsize:
            raise InvalidAsgConfigError('Autoscaling unit minsize ({0}) cannot be '
                                        'larger than maxsize ({1})'.format(self.minsize, self.maxsize))
