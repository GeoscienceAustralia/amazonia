#!/usr/bin/python3

from troposphere import Output, Ref, Join
from troposphere.s3 import Bucket


class S3(object):
    def __init__(self, unit_title, template, s3_access):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/s3.py
        s3_access = [Private,
                    PublicRead,
                    PublicReadWrite,
                    AuthenticatedRead,
                    BucketOwnerRead,
                    BucketOwnerFullControl,
                    LogDeliveryWrite]
        :param unit_title: Title of the s3 bucket unit
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param s3_access: A canned access control list (ACL) that grants predefined permissions to the bucket.
        For more information about canned ACLs http://docs.aws.amazon.com/AmazonS3/latest/dev/CannedACL.html
        Valid values: AuthenticatedRead | AwsExecRead | BucketOwnerRead | BucketOwnerFullControl |
            LogDeliveryWrite | Private | PublicRead | PublicReadWrite
        """

        title = (unit_title + 'AmzS3').lower()
        self.s3_b = template.add_resource(Bucket(title,
                                                 BucketName=title,
                                                 AccessControl=s3_access))

        template.add_output(Output(
            title,
            Value=Join('', [Ref(self.s3_b),
                            'is a managed S3 bucket, created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName')
                            ]),
            Description='Amazonia S3 Bucket'
        ))

