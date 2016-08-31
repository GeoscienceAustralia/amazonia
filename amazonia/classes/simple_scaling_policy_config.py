#!/usr/bin/python3


class SimpleScalingPolicyConfig(object):
    def __init__(self, name, description, metric_name, comparison_operator,
                 threshold, evaluation_periods, period, scaling_adjustment, cooldown):
        """
        Simple scaling policy config object

        :param name: Human readable name of sclaing policy
        :param description: Description of scaling policy
        :param metric_name: EC2 metric to evaluate against
        :param comparison_operator: GreaterThanOrEqualToThreshold | GreaterThanThreshold | LessThanThreshold
        | LessThanOrEqualToThreshold
        :param threshold: Metric threshold to evaluate against
        :param evaluation_periods: How many consecutive periods must pass before alarm/policy is triggered
        :param period: duration at threshold to trigger alarm/policy
        :param scaling_adjustment: negative or positive integer
        :param cooldown: period to wait before triggering again
        """
        self.name = name
        self.description = description
        self.metric_name = metric_name
        self.comparison_operator = comparison_operator
        self.threshold = threshold
        self.evaluation_periods = evaluation_periods
        self.period = period
        self.scaling_adjustment = scaling_adjustment
        self.cooldown = cooldown
