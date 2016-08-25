#!/usr/bin/python3

from nose.tools import *
from amazonia.classes.simple_scaling_policy_config import SimpleScalingPolicyConfig
from amazonia.classes.simple_scaling_policy import SimpleScalingPolicy
from troposphere import Template


def test_simple_scaling_policy():
    template = Template()

    heavyScalingPolicyConfig = SimpleScalingPolicyConfig(name='heavy - load',
                              description='When under heavy CPU load for five minutes, add two instances, wait 45 seconds',
                              metric_name='CPUUtilization',
                              comparison_operator='GreaterThanThreshold',
                              threshold='45',
                              evaluation_periods=1,
                              period=300,
                              scaling_adjustment=2,
                              cooldown=45)
    lightScalingPolicyConfig = SimpleScalingPolicyConfig(name='light - load',
                              description='When under light CPU load for 6 consecutive periods of five minutes, remove one instance, wait 120 seconds',
                              metric_name='CPUUtilization',
                              comparison_operator='LessThanOrEqualToThreshold',
                              threshold='15',
                              evaluation_periods=6,
                              period=300,
                              scaling_adjustment=-1,
                              cooldown=120)
    mediumScalingPolicyConfig = SimpleScalingPolicyConfig(name='medium - load',
                              description='When under medium CPU load for five minutes, add one instance, wait 45 seconds',
                              metric_name='CPUUtilization',
                              comparison_operator='GreaterThanOrEqualToThreshold',
                              threshold='25',
                              evaluation_periods=1,
                              period=300,
                              scaling_adjustment=1,
                              cooldown=120)

    heavyScalingPolicy = SimpleScalingPolicy(template=template,
                                             asg=None,
                                             scaling_policy_config=heavyScalingPolicyConfig)

    lightScalingPolicy = SimpleScalingPolicy(template=template,
                                             asg=None,
                                             scaling_policy_config=lightScalingPolicyConfig)

    mediumScalingPolicy = SimpleScalingPolicy(template=template,
                                             asg=None,
                                             scaling_policy_config=mediumScalingPolicyConfig)
