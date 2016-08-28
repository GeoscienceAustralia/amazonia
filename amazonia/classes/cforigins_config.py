#!/usr/bin/python3

from troposphere import cloudfront

class CFOriginsConfig(object):
    def __init__(self, template, domain_name, origin_id, origin_policy):
        """
        Class to abstract a Cloudfront Distribution Origin object of type S3 or Custom
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-origin.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param template: Troposphere stack to append resources to
        :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
        :param origin_id: An identifier for this origin (must be unique within this distribution)
        :param origin_policy: A dictionary containing origin-related variables
        """
        self.domain_name = domain_name
        self.origin_id = origin_id
        self.origin_policy = origin_policy

        if (origin_policy['type'] == 's3origin'):
            if origin_policy['origin_access_identity']:
                self.origin_access_identity = origin_policy['origin_access_identity']
        elif (origin_policy['type'] == 'customorigin'):
            if origin_policy['origin_protocol_policy']:
                self.origin_protocol_policy = origin_policy['origin_protocol_policy']
            else:
                raise InvalidTypeError('Error: Cloudfront custom origin {0} must contain an origin_protocol_policy.'.__format__(self.title))
        else:
            raise InvalidTypeError('Error: Cloudfront Origin type must be either s3origin or customorigin.')

class InvalidTypeError(Exception):
    def __init__(self, value):
        self.value = value
