#!/usr/bin/python3


class CFDistributionConfig(object):
    def __init__(self, aliases, comment, default_root_object, enabled, price_class,
                 target_origin_id, allowed_methods, cached_methods, trusted_signers,
                 query_string, forward_cookies, forwarded_headers, viewer_protocol_policy, min_ttl,
                 default_ttl, max_ttl, error_page_path, acm_cert_arn, minimum_protocol_version,
                 ssl_support_method):
        """
        Class containing configuration details for a Cloudfront Distribution
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param template: The current Cloudformation template (unused)
        :param network_config: The network_config of this stack (unused)
        :param aliases: A list of DNS CNAME aliases
        :param comment: A description for the distribution
        :param default_root_object: The object (e.g. index.html) that should be provided when the root URL is requested
        :param enabled: Controls whether the distribution is enabled to access user requests
        :param price_class: The price class that corresponds with the maximum price to be paid for the service
        :param target_origin_id: Value of the unique ID for the default cache behavior of this distribution
        :param allowed_methods: List of HTTP methods that can be passed to the origin
        :param cached_methods: List of HTTP methods for which Cloudfront caches responses
        :param trusted_signers: List of AWS accounts that can create signed URLs in order to access private content
        :param query_string: indicates whether to forward query strings to the origin
        :param forward_cookies: Which cookies to forward to the origin
        :param forwarded_headers: List of headers to forward to the origin
        :param viewer_protocol_policy: The protocol that users can use to access origin files
        :param min_ttl: The minimum amount of time objects should stay in the cache
        :param default_ttl: The default amount of time objects stay in the cache
        :param max_ttl: The maximum amount of time objects should stay in the cache
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
        self.target_origin_id = target_origin_id
        self.allowed_methods = allowed_methods
        self.cached_methods = cached_methods
        self.trusted_signers = trusted_signers if trusted_signers else []
        self.query_string = query_string
        self.forward_cookies = forward_cookies
        self.forwarded_headers = forwarded_headers
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.error_page_path = error_page_path
        self.acm_cert_arn = acm_cert_arn
        self.minimum_protocol_version = minimum_protocol_version
        self.ssl_support_method = ssl_support_method
