#!/usr/bin/python3

from troposphere import cloudfront, ImportValue


class CloudfrontConfigError(Exception):
    """
    Error thrown Cloudfront objects are misconfigured
    """

    def __init__(self, value):
        self.value = value


class CFDistribution(object):
    def __init__(self, title, template, cf_origins_config, cf_cache_behavior_config,
                 cf_distribution_config):
        """
        Class to abstract a Cloudfront Distribution object
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distributionconfig.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/cloudfront.py
        :param title: title of the Cloudfront Distribution and associated resources to be used in cloud formation
        :param template: Troposphere stack to append resources to
        :param cf_origins_config: A list of CFOriginsConfig objects
        :param cf_cache_behavior_config: A list of CFCacheBehavior objects
        :param cf_distribution_config: A CFDistributionConfig object
        """
        self.origins = []
        self.cache_behaviors = []
        self.default_cache_behavior = cloudfront.DefaultCacheBehavior()

        # Populate origins
        self.add_origins(title, cf_origins_config)
        # Populate cache_behaviors
        self.add_cache_behaviors(title, cf_cache_behavior_config)

        # Set distribution-wide parameters
        self.cf_dist = cloudfront.DistributionConfig(
            title + 'CfDistConfig',
            Aliases=cf_distribution_config.aliases,
            Comment=title,
            DefaultCacheBehavior=self.default_cache_behavior,
            CacheBehaviors=self.cache_behaviors,
            DefaultRootObject=cf_distribution_config.default_root_object,
            Enabled=cf_distribution_config.enabled,
            Origins=self.origins,
            PriceClass=cf_distribution_config.price_class
        )

        if cf_distribution_config.acm_cert_arn:
            self.cf_dist.ViewerCertificate = cloudfront.ViewerCertificate(
                AcmCertificateArn=cf_distribution_config.acm_cert_arn,
                SslSupportMethod='sni-only'
            )

        self.cf_dist = template.add_resource(cloudfront.Distribution(
            title,
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

            created_origin = cloudfront.Origin(
                '{0}Origin{1}'.format(title, number),
                DomainName=origin.domain_name,
                Id=origin.origin_id
            )

            if origin.origin_path:
                created_origin.OriginPath = origin.origin_path
            if origin.custom_headers:
                created_headers = []
                for k, v in origin.custom_headers.items():
                    if v is not None:
                        created_headers.append(
                            cloudfront.OriginCustomHeader(HeaderName=k, HeaderValue=v)
                        )
                created_origin.OriginCustomHeaders = created_headers

            # Set S3 config
            if origin.origin_policy['is_s3']:
                # Create S3Origin
                s3_origin_config = cloudfront.S3Origin()

                # Ensure variables exist
                if origin.origin_access_identity:
                    s3_origin_config.OriginAccessIdentity = origin.origin_access_identity

                # Set S3Origin
                created_origin.S3OriginConfig = s3_origin_config
            # Set Custom config
            else:

                created_origin.DomainName = self.get_custom_reference(origin.domain_name)

                # Create CustomOrigin
                custom_origin_config = cloudfront.CustomOrigin()

                # Ensure variables exist
                if origin.http_port:
                    custom_origin_config.HTTPPort = origin.http_port
                if origin.https_port:
                    custom_origin_config.HTTPSPort = origin.https_port
                if origin.origin_protocol_policy:
                    custom_origin_config.OriginProtocolPolicy = origin.origin_protocol_policy
                if origin.origin_ssl_protocols:
                    custom_origin_config.OriginSSLProtocols = origin.origin_ssl_protocols

                # Set CustomOrigin
                created_origin.CustomOriginConfig = custom_origin_config

            self.origins.append(created_origin)

    def add_cache_behaviors(self, title, cf_cache_behavior_config):
        """
        Create Cloudfront CacheBehavior objects and append to list of cache_behaviors
        :param title: Title of this Cloudfront Distribution
        :param cf_cache_behavior_config: list of CFCacheBehavior
        """

        default_cache_behavior_count = 0
        cache_behavior_count = 0

        for number, cache_behavior in enumerate(cf_cache_behavior_config):

            forwarded_values = cloudfront.ForwardedValues(
                Cookies=cloudfront.Cookies(
                    Forward=cache_behavior.forward_cookies
                ),
                QueryString=cache_behavior.query_string
            )
            if cache_behavior.forwarded_headers is not None:
                forwarded_values.Headers = cache_behavior.forwarded_headers

            cf_cache_behavior_params = {
                'AllowedMethods': cache_behavior.allowed_methods,
                'CachedMethods': cache_behavior.cached_methods,
                'Compress': False,
                'TargetOriginId': cache_behavior.target_origin_id,
                'ForwardedValues': forwarded_values,
                'TrustedSigners': cache_behavior.trusted_signers,
                'ViewerProtocolPolicy': cache_behavior.viewer_protocol_policy,
                'MinTTL': cache_behavior.min_ttl,
                'DefaultTTL': cache_behavior.default_ttl,
                'MaxTTL': cache_behavior.max_ttl,
                'SmoothStreaming': False
            }

            if cache_behavior.is_default:
                # Add default cache behavior
                self.default_cache_behavior = cloudfront.DefaultCacheBehavior(
                    '{0}DefaultCacheBehavior'.format(title),
                    **cf_cache_behavior_params
                )

                default_cache_behavior_count += 1
            else:
                # Append additional cache behaviors to list
                cf_cache_behavior_params['PathPattern'] = cache_behavior.path_pattern

                created_cache_behavior = cloudfront.CacheBehavior(
                    '{0}CacheBehavior{1}'.format(title, number),
                    **cf_cache_behavior_params
                )

                self.cache_behaviors.append(created_cache_behavior)
                cache_behavior_count += 1

            # if there is at least one cache behavior, there must be exactly one default cache behavior
            if cache_behavior_count > 0 and default_cache_behavior_count != 1:
                raise CloudfrontConfigError(
                    'Error: cf_distribution_unit {0} must have exactly one default cache behavior.'.format(title))

    def get_custom_reference(self, domain_name):
        """
        Define abstract method to be overridden by implementing classes
        :param domain_name: domain name of amazonia resource
        """
        raise NotImplementedError("Please Implement this method")


class CFDistributionLeaf(CFDistribution):
    def __init__(self, leaf_title, tree_name, template, cf_origins_config, cf_cache_behavior_config,
                 cf_distribution_config):
        """
        Create an Cloudfront distribution as a leaf, part of cross referenced stack
        :param leaf_title: title of the API Gateway as part of cross referenced stack
        :param tree_name: name of cross referenced stack
        :param template: Troposphere stack to append resources to
        :param cf_origins_config: A list of CFOriginsConfig objects
        :param cf_cache_behavior_config: A list of CFCacheBehavior objects
        :param cf_distribution_config: A CFDistributionConfig object
        """
        self.tree_name = tree_name
        super(CFDistributionLeaf, self).__init__(title=leaf_title, template=template,
                                                 cf_origins_config=cf_origins_config,
                                                 cf_cache_behavior_config=cf_cache_behavior_config,
                                                 cf_distribution_config=cf_distribution_config)

    def get_custom_reference(self, domain_name):
        """
        Return the endpoint from a different stack in the same tree
        :param domain_name: amazonia name of the endpoint
        :return: The endpoint of the specified amazonia object
        """
        return ImportValue(self.tree_name + '-' + domain_name + '-Endpoint')


class CFDistributionUnit(CFDistribution):
    def __init__(self, unit_title, template, stack_config, cf_origins_config, cf_cache_behavior_config,
                 cf_distribution_config):
        """
        Create a Cloudfront Distribution as a unit, part of an integrated stack
        :param unit_title: title of the API Gateway as part of an integrated stack
        :param template: troposphere template
        :param stack_config: shared stack configuration object to store generated API Gateway endpoint
        :param cf_origins_config: A list of CFOriginsConfig objects
        :param cf_cache_behavior_config: A list of CFCacheBehavior objects
        :param cf_distribution_config: A CFDistributionConfig object
        """
        self.stack_config = stack_config
        super(CFDistributionUnit, self).__init__(title=unit_title, template=template,
                                                 cf_origins_config=cf_origins_config,
                                                 cf_cache_behavior_config=cf_cache_behavior_config,
                                                 cf_distribution_config=cf_distribution_config)

    def get_custom_reference(self, domain_name):
        """
        Return the endpoint from a different stack in the same stack
        :param domain_name: amazonia name of the endpoint
        :return: The endpoint of the specified amazonia object
        """
        return self.stack_config.endpoints[domain_name]
