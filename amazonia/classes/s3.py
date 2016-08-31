#!/usr/bin/python3
from troposphere import Output, Ref, Join, GetAtt
from troposphere.s3 import Bucket, BucketPolicy


class S3(object):
    def __init__(self, unit_title, template, s3_access, bucket_policy):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-policy.html
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
        :param bucket_policy: A dictionary object containing s3 bucket policy
        """

        title = (unit_title + 'AmzS3').lower()

        # Add S3 Bucket
        self.s3_b = template.add_resource(Bucket(title,
                                                 BucketName=title,
                                                 AccessControl=s3_access,
                                                 DeletionPolicy='Retain'))
        template.add_output(Output(
            title,
            Value=Join('', [Ref(self.s3_b),
                            ' is a managed AWS S3 bucket, created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName'),
                            ' at ',
                            GetAtt(self.s3_b, 'WebsiteURL')
                            ]),
            Description='Amazonia S3 Bucket'
        ))

        # Add S3 Bucket Policy
        s3_b_policy_name = ''.join([title, 'policy'])
        if bucket_policy:
            self.s3_b_policy = template.add_resource(BucketPolicy(s3_b_policy_name,
                                                                  Bucket=title,
                                                                  PolicyDocument=bucket_policy,
                                                                  DependsOn=[self.s3_b.title]))
