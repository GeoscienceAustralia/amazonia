from troposphere import Ref
from troposphere.autoscaling import ScalingPolicy
from troposphere.cloudwatch import MetricDimension, Alarm

from amazonia.classes.util import get_cf_friendly_name


class SimpleScalingPolicy(object):
    def __init__(self, template, asg, scaling_policy_config):
        """
        Simple scaling policy based upon ec2 metrics

        heavy-load
        cpu > 45 for 1 period of 300 seconds add two instances, 45 second cooldown

        light-load
        cpu <= 15 for 6 periods of 300 seconds remove one instance, 120 second cooldown

        medium-load
        cpu >= 25 for 1 period of 300 seconds add one instance, 45 second cooldown

        [name]
        [metric_name] [comparison_operator] [threshold] [evaluation_periods] [period] [scaling_adjustment] [cooldown]

        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-policy.html
        :param scaling_policy_config: simple scaling policy config object
        """

        cf_name = asg.title + get_cf_friendly_name(scaling_policy_config.name)

        scaling_policy = template.add_resource(ScalingPolicy(
            title=cf_name + 'Sp',
            AdjustmentType='ChangeInCapacity',
            AutoScalingGroupName=Ref(asg),
            Cooldown=scaling_policy_config.cooldown,
            ScalingAdjustment=scaling_policy_config.scaling_adjustment,
        ))

        template.add_resource(Alarm(
            title=cf_name + 'Cwa',
            AlarmActions=Ref(scaling_policy),
            AlarmDescription=scaling_policy_config.description,
            AlarmName=scaling_policy_config.name,
            ComparisonOperator=scaling_policy_config.comparison_operator,
            Dimensions=[MetricDimension(
                Name='AutoScalingGroupName',
                Value=Ref(asg)
            )],
            EvaluationPeriods=scaling_policy_config.evaluation_periods,
            MetricName=scaling_policy_config.metric_name,
            Namespace='AWS/EC2',
            Period=scaling_policy_config.period,
            Statistic='Average',
            Threshold=scaling_policy_config.threshold
        ))
