#!/usr/bin/python3

from troposphere import cloudfront

class CFOriginsConfig(object):
    def __init__(self, template, domain_name, origin_id, origin_policy):
        """

        """

        self.domain_name = domain_name
        self.origin_id = origin_id
        self.origin_policy = origin_policy

        if (origin_policy['type'] == 's3origin'):
            if origin_policy['origin_access_identity']:
                self.origin_access_identity = origin_policy['origin_access_identity']
        else:
            self.origin_protocol_policy = origin_policy['origin_protocol_policy']