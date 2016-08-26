#!/usr/bin/python3

from troposphere import Tags, Ref, Output, Join, GetAtt, cloudfront

class CFDistribution(object):
    def __init__(self, title, template, cforigins_config, cfcache_behaviors_config, cfdistribution_config):
        """

        """
        self.title = title + 'CFDist'
        self.origins = []
        self.cache_behaviors = []

        self.default_cache_behavior = self.add_default_cache_behavior(title, cfdistribution_config)

        # Populate origins
        self.add_origins(title, cforigins_config)
        # Populate cache_behaviors
        self.add_cache_behaviors(title, cfcache_behaviors_config)

        cfdist_params = {
            'Aliases' : cfdistribution_config.aliases,
            'Comment' : self.title,
            'DefaultCacheBehavior' : self.default_cache_behavior,
            'CacheBehaviors' : self.cache_behaviors,
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

    def add_origins(self, title, cforigins_config):
        for n, origin in enumerate(cforigins_config):

            if (origin.origin_policy['type'] == 's3origin'):
                # Create S3Origin
                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, n),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    S3OriginConfig=cloudfront.S3Origin(
                        OriginAccessIdentity=origin.origin_access_identity
                    )
                )
            else:
                # Create CustomOrigin
                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, n),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    CustomOriginConfig=cloudfront.CustomOrigin(
                        HTTPPort='80',
                        HTTPSPort='443',
                        # Add input checking to ensure protocol_policy is one of (allow-all, http-only, https-only)
                        OriginProtocolPolicy=origin.origin_protocol_policy,
                        OriginSSLProtocols=['TLSv1','TLSv1.1','TLSv1.2']
                    )
                )

            self.origins.append(created_origin)

    def add_cache_behaviors(self, title, cfcache_behaviors_config):
        for n, cache_behavior in enumerate(cfcache_behaviors_config):

            created_cache_behavior = cloudfront.CacheBehavior(
                '{0}CacheBehavior{1}'.format(title, n),
                AllowedMethods=cache_behavior.allowed_methods,
                CachedMethods=cache_behavior.cached_methods,
                Compress=False,
                TargetOriginId=cache_behavior.target_origin_id,
                ForwardedValues=cloudfront.ForwardedValues(
                    Cookies=cloudfront.Cookies(
                        Forward=cache_behavior.forward_cookies
                    ),
                    QueryString=False
                ),
                TrustedSigners=cache_behavior.trusted_signers,
                ViewerProtocolPolicy=cache_behavior.viewer_protocol_policy,
                MinTTL=cache_behavior.min_ttl,
                DefaultTTL=cache_behavior.default_ttl,
                MaxTTL=cache_behavior.max_ttl,
                PathPattern=cache_behavior.path_pattern,
                SmoothStreaming=False
            )

            self.cache_behaviors.append(created_cache_behavior)

    def add_default_cache_behavior(self, title, cfdistribution_config):

        return cloudfront.DefaultCacheBehavior(
            TargetOriginId=cfdistribution_config.target_origin_id,
            CachedMethods=cfdistribution_config.cached_methods,
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=cfdistribution_config.trusted_signers,
            ViewerProtocolPolicy=cfdistribution_config.viewer_protocol_policy,
            MinTTL=cfdistribution_config.min_ttl,
            DefaultTTL=cfdistribution_config.default_ttl,
            MaxTTL=cfdistribution_config.max_ttl
        )