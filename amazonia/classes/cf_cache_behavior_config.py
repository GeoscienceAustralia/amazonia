#!/usr/bin/python3


class CFCacheBehavior(object):
    def __init__(self, path_pattern, allowed_methods, cached_methods, target_origin_id,
                 forward_cookies, forwarded_headers, viewer_protocol_policy, min_ttl, default_ttl,
                 max_ttl, trusted_signers):
        """
        Class containing cache behavior details for a Cloudfront origin
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-cachebehavior.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
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
        """
        self.path_pattern = path_pattern
        self.allowed_methods = allowed_methods
        self.cached_methods = cached_methods
        self.target_origin_id = target_origin_id
        self.forward_cookies = forward_cookies
        self.forwarded_headers = forwarded_headers
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.trusted_signers = trusted_signers
