#!/usr/bin/python3

from troposphere import GetAtt

class CFOriginsConfig(object):
    def __init__(self, domain_name, origin_id, origin_path, custom_headers, origin_policy):
        """
        Class to abstract a Cloudfront Distribution Origin object of type S3 or Custom
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-origin.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
        :param origin_id: An identifier for this origin (must be unique within this distribution)
        :param origin_path: An optional directory path
        :param custom_headers: A list of custom headers to forward to this origin
        :param origin_policy: A dictionary containing origin-related variables
        """

        self.domain_name = domain_name
        self.origin_id = origin_id
        self.origin_path = origin_path if origin_path else None
        self.custom_headers = custom_headers if custom_headers else {}
        self.origin_policy = origin_policy
        self.origin_access_identity = None
        self.origin_protocol_policy = None
        self.http_port = None
        self.https_port = None
        self.origin_ssl_protocols = None

        if origin_policy['is_s3']:
            # Set S3 origin variables

            self.origin_access_identity = origin_policy['origin_access_identity']
        else:
            # Check if custom origin variables exist, and set them if they do
            self.origin_protocol_policy = origin_policy['origin_protocol_policy']
            self.http_port = origin_policy['http_port']
            self.https_port = origin_policy['https_port']
            self.origin_ssl_protocols = origin_policy['origin_ssl_protocols']