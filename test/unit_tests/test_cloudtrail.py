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
        cloud_trail = (Cloudtrail(name, template))
        assert_equals(cloud_trail.s3_b_trail.s3_b.title, (name + 'trail' + 'amzs3').lower())


def test_s3_bucket_policy():
    """
    To test that bucket policy is applied is passed in
    """
    template = Template()

    cloud_trail = (Cloudtrail('MyTrail', template))

    # Test policy matches
    assert_equals(type(cloud_trail.s3_b_trail.s3_b_policy.PolicyDocument), dict)

    # Test bucket name is policy matches
    assert_equals(cloud_trail.s3_b_trail.s3_b_policy.Bucket, 'mytrailtrailamzs3')


def test_s3_bucket_name_in_cloudtrail():
    """
    To test the s3 bucket name in cloudtrail
    """
    template = Template()

    cloud_trail = (Cloudtrail('MyTrail', template))
    assert_equals(cloud_trail.trail.S3BucketName, 'mytrailtrailamzs3')
