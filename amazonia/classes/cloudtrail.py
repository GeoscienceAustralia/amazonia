#!/usr/bin/python3

from troposphere import Output, Join, Ref
from troposphere.cloudtrail import Trail
from amazonia.classes.s3 import S3


class Cloudtrail(object):
    def __init__(self, unit_title, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudtrail.py
        """

        title = unit_title + 'Trail'

        policy = {
            # "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": 'mycloudtrailamzs3'
                },
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::mytrailamzs3/AWSLogs/123456789/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }
            ]
        }

        # Create S3 Bucket for Cloud Trail Log
        self.s3_b_trail = S3(unit_title=title,
                             template=template,
                             s3_access='BucketOwnerFullControl',
                             bucket_policy=policy)

        # Create Cloudtrail Trail
        self.trail = template.add_resource(Trail(title,
                                                 IsLogging=True,
                                                 S3BucketName=self.s3_b_trail.s3_b.title,
                                                 S3KeyPrefix='cloudtrail',
                                                 EnableLogFileValidation=True,
                                                 IncludeGlobalServiceEvents=True,
                                                 IsMultiRegionTrail=True
                                                 ))
        self.trail.DependsOn = [self.s3_b_trail.s3_b.title]

        template.add_output(Output(
            title,
            Value=Join('', [Ref(self.trail),
                            ' is a managed AWS Cloudtrail Trail, created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName')
                            ]),
            Description='Amazonia Cloudtrail'
        ))

