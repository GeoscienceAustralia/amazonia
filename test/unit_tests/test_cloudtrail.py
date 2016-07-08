from nose.tools import *
from amazonia.classes.cloudtrail import Cloudtrail
from troposphere import Template, Join, s3
"""
Tests the functions of the Cloudtrail class
"""


def test_s3_title():
    """
    Test s3 bucket title is as expected
    """
    template = Template()

    test_s3_names = ['MyTest', 'Tests3', 'Supers3bucket']

    for name in test_s3_names:
        cloud_trail = (Cloudtrail(name, template)
        assert_equals(cloud_trail.s3_b.title, (name + 'amzs3').lower())


def test_s3_bucket_policy():
    """
    To test that bucket policy is applied is passed in
    """


def test_s3_bucket_name_in_cloudtrail():
    """
    To test the s3 bucket name in cloudtrail
    """


def test_cloudtrail_depends_on_s3_bucket_policy()