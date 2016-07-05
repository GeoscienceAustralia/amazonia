#!/usr/bin/python3

from troposphere import Output, Ref, Join
from troposphere.sns import Topic


class SNS(object):
    def __init__(self, unit_title, template, topic_name, display_name):
        """
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sns-topic.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/sns.py
        :param unit_title: Title of the sns unit
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param topic_name
        :param display_name
        """
        title = unit_title + 'sns'
        self.sns_topic = template.add_resource(Topic(title, TopicName=topic_name, DisplayName=display_name))

        template.add_output(Output(
            title,
            Value=Ref(self.sns_topic),
            Description=Join('', ['SNS topic, created with Amazonia as part of ',
                                  Ref('AWS::StackName')
                                  ])
        ))
