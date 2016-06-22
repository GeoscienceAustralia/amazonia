from nose.tools import *
from amazonia.classes.s3 import S3
from troposphere import Template
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
        s3_bucket = S3('TestAccess' + str(num), template, access)
        assert_equals(s3_bucket.s3_b.AccessControl, access)


def test_s3_title():
    """
    To test title is properly set in s3Bucket
    """
    template = Template()

    test_s3_names = ['MyTest', 'Tests3', 'Supers3bucket']

    for name in test_s3_names:
        s3_bucket = S3(name, template, 'Private')
        assert_equals(s3_bucket.s3_b.title, name + 's3')
