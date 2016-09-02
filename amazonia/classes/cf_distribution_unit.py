#!/usr/bin/python3

from troposphere import Tags, Ref, Output, Join, GetAtt, cloudfront

class CFDistributionUnit(object):
    def __init__(self, unit_title, template, network_config, cf_origins_config, cf_cache_behavior_config,
                 cf_distribution_config):
        """
        Class to abstract a Cloudfront Distribution object
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param title: The title of this Cloudfront distribution
        :param template: Troposphere stack to append resources to
        :param cf_origins_config: A list of CFOriginsConfig objects
        :param cf_cache_behavior_config: A list of CFCacheBehavior objects
        :param cf_distribution_config: A CFDistributionConfig object
        :param network_config: Network config information (unused)
        """

        self.title = unit_title + 'CFDist'
        self.dependencies = []
        self.origins = []
        self.cache_behaviors = []
        self.default_cache_behavior = cloudfront.DefaultCacheBehavior()

        self.default_cache_behavior = self.add_default_cache_behavior(self.title, cf_distribution_config)

        # Populate origins
        self.add_origins(self.title, cf_origins_config)
        # Populate cache_behaviors
        self.add_cache_behaviors(self.title, cf_cache_behavior_config)

        # Set distribution-wide parameters
        self.cf_dist = cloudfront.DistributionConfig(
            self.title,
            Aliases=cf_distribution_config.aliases,
            Comment=self.title,
            DefaultCacheBehavior=self.default_cache_behavior,
            CacheBehaviors=self.cache_behaviors,
            DefaultRootObject=cf_distribution_config.default_root_object,
            Enabled=cf_distribution_config.enabled,
            Origins=self.origins,
            PriceClass=cf_distribution_config.price_class
        )

        self.cf_dist = template.add_resource(cloudfront.Distribution(
            self.title,
            DistributionConfig=self.cf_dist
            )
        )

    def add_origins(self, title, cf_origins_config):
        """
        Create Cloudfront Origin objects and append to list of origins
        :param title: Title of this Cloudfront Distribution
        :param cf_origins_config: List of CFOrigins
        """
        for number, origin in enumerate(cf_origins_config):

            if origin.origin_policy['is_s3']:
                # Create S3Origin
                s3_origin_config=cloudfront.S3Origin()

                # Ensure variables exist
                if hasattr(origin, 'origin_access_identity'):
                    s3_origin_config.OriginAccessIdentity=origin.origin_access_identity

                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, number),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    S3OriginConfig=s3_origin_config
                )
            else:
                # Create CustomOrigin
                custom_origin_config = cloudfront.CustomOrigin()

                # Ensure variables exist
                if hasattr(origin, 'http_port'):
                    custom_origin_config.HTTPPort=origin.http_port
                if hasattr(origin, 'https_port'):
                    custom_origin_config.HTTPSPort=origin.https_port
                if hasattr(origin, 'origin_protocol_policy'):
                    custom_origin_config.OriginProtocolPolicy=origin.origin_protocol_policy
                # TODO: Uncomment when pip troposphere supports OriginSSLProtocols
                #if hasattr(origin, 'origin_ssl_protocols'):
                    #custom_origin_config.OriginSSLProtocols=origin.origin_ssl_protocols

                created_origin = cloudfront.Origin(
                    '{0}Origin{1}'.format(title, number),
                    DomainName=origin.domain_name,
                    Id=origin.origin_id,
                    CustomOriginConfig=custom_origin_config
                )

            self.origins.append(created_origin)

    def add_cache_behaviors(self, title, cf_cache_behavior_config):
        """
        Create Cloudfront CacheBehavior objects and append to list of cache_behaviors
        :param title: Title of this Cloudfront Distribution
        :param cf_cache_behavior_config: list of CFCacheBehavior
        """

        for number, cache_behavior in enumerate(cf_cache_behavior_config):

            created_cache_behavior = cloudfront.CacheBehavior(
                '{0}CacheBehavior{1}'.format(title, number),
                AllowedMethods=cache_behavior.allowed_methods,
                CachedMethods=cache_behavior.cached_methods,
                Compress=False,
                TargetOriginId=cache_behavior.target_origin_id,
                ForwardedValues=cloudfront.ForwardedValues(
                    Cookies=cloudfront.Cookies(
                        Forward=cache_behavior.forward_cookies
                    ),
                    Headers=cache_behavior.forwarded_headers,
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

    def add_default_cache_behavior(self, title, cf_distribution_config):
        """
        Create Cloudfront DefaultCacheBehavior object
        :param title: Title of this Cloudfront distribution
        :param cf_distribution_config: Object containing the default cache behavior of this distribution
        :return: Returns the created DefaultCacheBehavior object
        """
        return cloudfront.DefaultCacheBehavior(
            TargetOriginId=cf_distribution_config.target_origin_id,
            CachedMethods=cf_distribution_config.cached_methods,
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=cf_distribution_config.trusted_signers,
            ViewerProtocolPolicy=cf_distribution_config.viewer_protocol_policy,
            MinTTL=cf_distribution_config.min_ttl,
            DefaultTTL=cf_distribution_config.default_ttl,
            MaxTTL=cf_distribution_config.max_ttl,
            # TODO: Uncomment when pip troposphere supports ViewerCertificate
            #ViewerCertificate=cloudfront.ViewerCertificate(
                #AcmCertificateArn=cf_distribution_config.acm_cert_arn,
                #MinimumProtocolVersion=cf_distribution_config.minimum_protocol_version,
                #SslSupportMethod=cf_distribution_config.ssl_support_method
            #)
        )


    def get_dependencies(self):
        """
        :return: returns an empty list as a cfdistribution has no upstream dependencies
        """
        return self.dependencies
