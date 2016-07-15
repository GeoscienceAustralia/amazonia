from nose.tools import *
from amazonia.classes.sns import SNS
from troposphere import Template

"""
Tests the functions of the SNS class
"""


def test_sns():
    """
    Test SNS object is created with the correct structure
    """
    template = Template()
    title = 'test'
    topic_name = 'test_topic'
    display_name = 'test_display_name'

    sns_topic = SNS(unit_title=title, template=template, topic_name=topic_name, display_name=display_name)

    assert_equals(sns_topic.sns_topic.title, (title + 'sns').lower())
    assert_equals(sns_topic.sns_topic.TopicName, topic_name)
    assert_equals(sns_topic.sns_topic.DisplayName, display_name)

    assert_equals(len(template.outputs), 1)
