#!/usr/bin/python3


class CFDistributionConfig(object):
    def __init__(self, aliases, comment, default_root_object, enabled, price_class,
                 error_page_path, acm_cert_arn, minimum_protocol_version,
                 ssl_support_method):
        """
        Class containing configuration details for a Cloudfront Distribution
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param aliases: A list of DNS CNAME aliases
        :param comment: A description for the distribution
        :param default_root_object: The object (e.g. index.html) that should be provided when the root URL is requested
        :param enabled: Controls whether the distribution is enabled to access user requests
        :param price_class: The price class that corresponds with the maximum price to be paid for the service
        :param error_page_path: The error page that should be served when an HTTP error code is returned
        :param acm_cert_arn: ARN of the ACM certificate
        :param minimum_protocol_version: The minimum version of the SSL protocol that should be used for HTTPS
        :param ssl_support_method: Specifies how Cloudfront serves HTTPS requests
        """

        self.aliases = aliases
        self.comment = comment
        self.default_root_object = default_root_object
        self.enabled = enabled
        self.price_class = price_class
        self.error_page_path = error_page_path
        self.acm_cert_arn = acm_cert_arn
        self.minimum_protocol_version = minimum_protocol_version
        self.ssl_support_method = ssl_support_method
