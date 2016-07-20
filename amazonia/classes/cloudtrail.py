#!/usr/bin/python3

from troposphere import Output, Join, Ref
from troposphere.cloudtrail import Trail
from amazonia.classes.s3 import S3


class Cloudtrail(object):
    def __init__(self, unit_title, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudtrail.py
        :param unit_title: Name of the Cloudtrail Unit e.g. MyCloudTrail
        :param template: The troposphere template to add the Cloudtrail and s3 troposphere objects to.
        """

        trail_title = unit_title + 'Trail'
        s3_title = (trail_title + 'AmzS3').lower()

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
                                                  s3_title,
                                                  "/AWSLogs/",
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

        # Create S3 Bucket for Cloud Trail Log
        self.s3_b_trail = S3(unit_title=trail_title,
                             template=template,
                             s3_access='BucketOwnerFullControl',
                             bucket_policy=policy)

        # Create Cloudtrail Trail
        self.trail = template.add_resource(Trail(trail_title,
                                                 IsLogging=True,
                                                 S3BucketName=self.s3_b_trail.s3_b.title,
                                                 EnableLogFileValidation=True,
                                                 IncludeGlobalServiceEvents=True,
                                                 IsMultiRegionTrail=True,
                                                 DependsOn=[self.s3_b_trail.s3_b_policy.title]
                                                 ))

        template.add_output(Output(
            trail_title,
            Value=Join('', [Ref(self.trail),
                            ' is a managed AWS Cloudtrail Trail, created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName')
                            ]),
            Description='Amazonia Cloudtrail'
        ))

