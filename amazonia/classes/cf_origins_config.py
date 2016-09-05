#!/usr/bin/python3

from troposphere import cloudfront

class CFOriginsConfig(object):
    def __init__(self, domain_name, origin_id, origin_policy):
        """
        Class to abstract a Cloudfront Distribution Origin object of type S3 or Custom
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-origin.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param template: Troposphere stack to append resources to
        :param network_config: The network_config of this stack (unused)
        :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
        :param origin_id: An identifier for this origin (must be unique within this distribution)
        :param origin_headers: A list of custom headers to forward to this origin
        :param origin_policy: A dictionary containing origin-related variables
        """

        self.domain_name = domain_name
        self.origin_id = origin_id
        self.origin_policy = origin_policy

        if origin_policy['is_s3']:
            # Set S3 origin variables

            self.origin_access_identity = origin_policy['origin_access_identity']

        else:
            # Check if custom origin variables exist, and set them if they do
            self.origin_protocol_policy = origin_policy['origin_protocol_policy']
            self.http_port = origin_policy['http_port']
            self.https_port = origin_policy['https_port']
            self.origin_ssl_protocols = origin_policy['origin_ssl_protocols']
