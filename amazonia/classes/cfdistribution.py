#!/usr/bin/python3

from troposphere import Tags, Ref, Output, Join, GetAtt, cloudfront

class CFDistribution(object):
    def __init__(self, title, template, cforigins_config, cfcache_behaviors_config, cfdistribution_config):
        """

        """
        self.title = title + 'CFDist'
        self.origins = []

        for n, origin in enumerate(cforigins_config):

            created_origin = cloudfront.Origin(
                '{0}Origin{1}'.format(title, n),
                DomainName=origin.domain_name,
                Id=origin.origin_id,
                S3OriginConfig=cloudfront.S3Origin(
                    OriginAccessIdentity=origin.origin_access_identity
                )
            )
            self.origins.append(created_origin)

        self.default_cache_behavior = {
            'TargetOriginId': cfdistribution_config.target_origin_id,
            'CachedMethods': cfdistribution_config.cached_methods,
            'Compress':False,
            'ForwardedValues':cloudfront.ForwardedValues(
                QueryString=False
            ),
            'CustomErrorResponses': cloudfront.CustomErrorResponse(
                ErrorCode='404',
                ResponsePagePath=cfdistribution_config.error_page_path,
                ResponseCode='200',
                ErrorCachingMinTTL=0,
            ),
            'TrustedSigners': cfdistribution_config.trusted_signers,
            'ViewerProtocolPolicy': cfdistribution_config.viewer_protocol_policy,
            'MinTTL': cfdistribution_config.min_ttl,
            'MaxTTL': cfdistribution_config.max_ttl,
            'DefaultTTL': cfdistribution_config.default_ttl,
        }

        cfdist_params = {
            'Aliases' : cfdistribution_config.aliases,
            'Comment' : self.title,
            'DefaultCacheBehavior' : Ref(self.default_cache_behavior),
            'CacheBehaviors' : cfcache_behaviors_config,
            'DefaultRootObject' : cfdistribution_config.default_root_object,
            'Enabled' : True,
            'Origins' : self.origins,
            'PriceClass' : 'PriceClass_All',
        }

        self.cf_dist = template.add_resource(cloudfront.DistributionConfig(
                self.title,
                **cfdist_params
            )
        )