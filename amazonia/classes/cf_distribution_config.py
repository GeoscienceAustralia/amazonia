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


class CFCacheBehaviorConfig(object):
    def __init__(self, is_default, path_pattern, allowed_methods, cached_methods, target_origin_id,
                 forward_cookies, forwarded_headers, viewer_protocol_policy, min_ttl, default_ttl,
                 max_ttl, trusted_signers, query_string):
        """
        Class containing cache behavior details for a Cloudfront origin
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-cachebehavior.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param is_default: Indicates whether this is the default cache behavior
        :param path_pattern: The pattern to which this cache behavior applies
        :param allowed_methods: List of HTTP methods that can be passed to the origin
        :param cached_methods: List of HTTP methods for which Cloudfront caches responses
        :param target_origin_id: Value of the unique ID for the default cache behavior of this distribution
        :param forward_cookies: Which cookies to forward to the origin
        :param forwarded_headers: List of headers to forward to the origin
        :param viewer_protocol_policy: The protocol that users can use to access origin files
        :param min_ttl: The minimum amount of time objects should stay in the cache
        :param default_ttl: The default amount of time objects stay in the cache
        :param max_ttl: The maximum amount of time objects should stay in the cache
        :param forward_cookies: boolean to forward cookies to origin
        :param trusted_signers: list of identifies that are trusted to sign cookies on behalf of this behavior
        :param query_string: boolean indicating whether to forward query strings to the origin
        """

        self.is_default = is_default
        self.path_pattern = path_pattern if path_pattern else None
        self.allowed_methods = allowed_methods
        self.cached_methods = cached_methods
        self.target_origin_id = target_origin_id
        self.forward_cookies = forward_cookies
        self.forwarded_headers = forwarded_headers
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.trusted_signers = trusted_signers if trusted_signers else []
        self.query_string = query_string
