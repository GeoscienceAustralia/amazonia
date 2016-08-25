#!/usr/bin/python3

from troposphere import cloudfront

class CFOriginsConfig(object):
    def __init__(self, template, domain_name, origin_id, origin_access_identity):
                 #origin_protocol_policy):
        """

        """

        self.domain_name = domain_name
        self.origin_id = origin_id
        self.origin_access_identity = origin_access_identity

        # if domain_name.split('.')[:-3] == 's3':
        #     self.s3_origin_config = template.add_resource(cloudfront.S3Origin())
        #
        #     if origin_access_identity:
        #         self.s3_origin_config.OriginAccessIdentity = origin_access_identity
        #
        #     self.origin = template.add_resource(cloudfront.Origin(
        #         DomainName=domain_name,
        #         Id=origin_id,
        #         S3OriginConfig=self.s3_origin_config,
        #     ))
        #
        # else:
        #     self.origin = template.add_resource(cloudfront.Origin(
        #             DomainName=domain_name,
        #             Id=origin_id,
        #             CustomOriginConfig=cloudfront.CustomOrigin(
        #                 HTTPPort='80',
        #                 HTTPSPort='443',
        #                 OriginProtocolPolicy=origin_protocol_policy,
        #                 OriginSSLProtocols=['TLSv1', 'TLSv1.1', 'TLSv1.2']
        #             )
        #         )
        #     )