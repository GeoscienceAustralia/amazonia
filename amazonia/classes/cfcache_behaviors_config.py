#!/usr/bin/python3


class CFCacheBehaviors(object):
    def __init__(self, path_pattern, allowed_methods, cached_methods, target_origin_id,
                 forward_cookies, viewer_protocol_policy, min_ttl, default_ttl, max_ttl,
                 trusted_signers):
        """

        """

        self.path_pattern = path_pattern
        self.allowed_methods = allowed_methods
        self.cached_methods = cached_methods
        self.target_origin_id = target_origin_id
        self.forward_cookies = forward_cookies
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.trusted_signers = trusted_signers