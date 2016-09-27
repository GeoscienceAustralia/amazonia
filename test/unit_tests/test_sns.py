from nose.tools import *
from amazonia.classes.sns import SNS
from troposphere import Template, Join

"""
Tests the functions of the SNS class
"""


def test_sns():
    """
    Test SNS object is created with the correct structure
    """
    template = Template()

    sns_topic = SNS(template=template)

    assert_equals(sns_topic.trop_topic.title, 'SnsTopic')
    assert_is(type(sns_topic.trop_topic.DisplayName), Join)

