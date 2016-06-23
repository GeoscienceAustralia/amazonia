#!/usr/bin/python3

from troposphere.cloudtrail import Trail
from amazonia.classes.s3 import S3


class Cloudtrail(object):
    def __init__(self, unit_title, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudtrail.py
        """

        title = unit_title + 'Trail'

        # S3 Bucket for Cloud Trail Log
        self.s3_b_trail = S3(unit_title=title,
                             template=template,
                             s3_access='LogDeliveryWrite')

        # Cloudtrail
        self.trail = template.add_resource(Trail(title,
                                                 IsLogging=True,
                                                 S3BucketName=self.s3_b_trail.s3_b.title,
                                                 S3KeyPrefix='cloudtrail',
                                                 EnableLogFileValidation=True,
                                                 IncludeGlobalServiceEvents=True,
                                                 IsMultiRegionTrail=True
                                                 ))


