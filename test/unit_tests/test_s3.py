from nose.tools import *
from amazonia.classes.s3 import S3
from troposphere import Template, Join, s3
"""
Tests the functions of the s3 bucket class
"""


def test_s3_access():
    """
    Test s3 Bucket Access Control values
    """
    template = Template()

    access_list = ['Private',
                   'PublicRead',
                   'PublicReadWrite',
                   'AuthenticatedRead',
                   'BucketOwnerRead',
                   'BucketOwnerFullControl',
                   'LogDeliveryWrite'
                   ]

    for num, access in enumerate(access_list):
        s3_bucket = S3('TestAccess' + str(num), template, access, '')
        assert_equals(s3_bucket.s3_b.AccessControl, access)


def test_s3_title():
    """
    To test title is properly set in s3Bucket
    """
    template = Template()

    test_s3_names = ['MyTest', 'Tests3', 'Supers3bucket']

    for name in test_s3_names:
        s3_bucket = S3(name, template, 'Private', '')
        assert_equals(s3_bucket.s3_b.title, (name + 'amzs3').lower())


def test_s3_bucket_policy():
    """
    To test that bucket policy is applied if passed in
    """
    template = Template()

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": "arn:aws:s3:::mycloudtrailamzs3"
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": Join('', ["arn:aws:s3:::",
                                      'WithPolicy',
                                      "/cloudtrail/AWSLogs/",
                                      {'Ref': 'AWS::AccountId'},
                                      "/*"]),
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                }
            }
        ]
    }

    s3_bucket = S3('WithPolicy', template, 'Private', policy)

    # Test policy exists
    assert_is(type(s3_bucket.s3_b_policy), s3.BucketPolicy)
    # Test that s3 bucket used for policy is right
    assert_equals(s3_bucket.s3_b_policy.Bucket, s3_bucket.s3_b.title)


@raises(AttributeError)
def test_s3_bucket_without_policy():
    """
    To test that bucket policy is applied if passed in
    """

    template = Template()

    s3_bucket = S3('WithoutPolicy', template, 'Private', '')
    assert_is_not_none(s3_bucket.s3_b_policy)


