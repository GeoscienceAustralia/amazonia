#!/usr/bin/python3

from troposphere import Ref, Join, cloudwatch
from troposphere.sns import Topic, Subscription


class SNS(object):
    def __init__(self, template):
        """
        AWS: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/sns.py
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        """
        title = 'SnsTopic'

        self.template = template
        self.trop_topic = self.template.add_resource(Topic(title,
                                                           DisplayName=Join('', [Ref('AWS::StackName'),
                                                                                 'Notifications'])))
        self.subscriptions = []
        self.alarms = []

    def add_subscription(self, endpoint, protocol):
        """
        Adds a subscription to this sns topic.
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-subscription.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/sns.py
        :param endpoint: the endpoint to send the notification to (eg 'my@email.com')
        :param protocol: the protocol to use to send the notification (eg 'email')
        """
        sub = Subscription(
            '{0}Subscription{1}'.format(self.trop_topic.title, str(len(self.subscriptions))),
            Endpoint=endpoint,
            Protocol=protocol
        )

        self.subscriptions.append(sub)
        self.trop_topic.Subscription = self.subscriptions

    def add_alarm(self, description, metric, namespace, threshold, instance):
        """
        Adds an alarm to this sns topic. For this to be useful, subscriptions must be added to this topic
        using the add_subscription function above.
        :param description: A description for the Alarm being created
        :param metric: The metric to track and alarm on.
        :param namespace: the namespace that the provided metric belongs to.
        :param threshold: The threshold to alarm on
        :param instance: an instance to refer to in particular
        """

        alarm = cloudwatch.Alarm(
                    '{0}Alarm{1}'.format(self.trop_topic.title, str(len(self.alarms))),
                    AlarmDescription=description,
                    AlarmActions=[Ref(self.trop_topic.title)],
                    OKActions=[Ref(self.trop_topic.title)],
                    MetricName=metric,
                    Namespace=namespace,
                    Threshold=threshold,
                    ComparisonOperator="GreaterThanOrEqualToThreshold",
                    EvaluationPeriods='1',
                    Period='300',
                    Statistic='Sum',
                    DependsOn=self.trop_topic.title,
                    Dimensions=[cloudwatch.MetricDimension(Name='InstanceId', Value=Ref(instance))]
                )

        self.alarms.append(alarm)
        self.template.add_resource(alarm)
