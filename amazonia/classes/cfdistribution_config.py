#!/usr/bin/python3


class CFDistributionConfig(object):
    def __init__(self, aliases, comment, default_root_object, enabled, price_class,
                 target_origin_id, allowed_methods, cached_methods, trusted_signers,
                 viewer_protocol_policy, min_ttl, default_ttl, max_ttl, error_page_path):
        """

        """

        self.aliases = aliases
        self.comment = comment
        self.default_root_object = default_root_object
        self.enabled = enabled
        self.price_class = price_class
        self.target_origin_id = target_origin_id
        self.allowed_methods = allowed_methods
        self.cached_methods = cached_methods
        self.trusted_signers = trusted_signers
        self.viewer_protocol_policy = viewer_protocol_policy
        self.min_ttl = min_ttl
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.error_page_path = error_page_path