#!/usr/bin/python3

from amazonia.classes.util import detect_unencrypted_access_keys


class InvalidAsgConfigError(Exception):
    """
    Exception if invalid properties are supplied
    """
    def __init__(self, value):
        self.value = value


class AsgConfig(object):
    def __init__(self, health_check_grace_period,
                 health_check_type, minsize, maxsize, image_id, instance_type, userdata,
                 iam_instance_profile_arn, block_devices_config, simple_scaling_policy_config,
                 ec2_scheduled_shutdown, pausetime):
        """
        Simple config class to contain autoscaling group related parameters
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param userdata: Instance boot script
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param health_check_grace_period: The amount of time to wait for an instance to start before checking health
        :param health_check_type: The type of health check. currently 'ELB' or 'EC2' are the only valid types.
        :param block_devices_config: List containing block device mappings
        :param simple_scaling_policy_config: List containing scaling policies
        :param ec2_scheduled_shutdown: True/False for whether to schedule shutdown for EC2 instances outside work hours
        :param pausetime: number of minutes as an int. Time between building an instance and taking down the old one
        """
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
        self.ec2_scheduled_shutdown = ec2_scheduled_shutdown
        self.pausetime = pausetime

        # check for insecure variables
        if self.userdata is not None:
            detect_unencrypted_access_keys(self.userdata)

        # Validate that minsize is less than maxsize
        if int(self.minsize) > int(self.maxsize):
            raise InvalidAsgConfigError('Autoscaling unit minsize ({0}) cannot be '
                                        'larger than maxsize ({1})'.format(self.minsize, self.maxsize))
