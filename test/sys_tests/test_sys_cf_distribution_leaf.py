#!/usr/bin/python3

from amazonia.classes.cf_distribution_config import CFDistributionConfig, CFCacheBehaviorConfig, CFOriginsConfig
from amazonia.classes.amz_cf_distribution import CFDistributionLeaf
from troposphere import Template


def main():
    template = Template()

    origins = [
        CFOriginsConfig(
            domain_name='app2',
            origin_id='app2',
            origin_path='',
            custom_headers=[],
            origin_policy={
                'is_s3': False,
                'origin_protocol_policy': 'http-only',
                'http_port': 80,
                'https_port': 443,
                'origin_ssl_protocols': ['TLSv1', 'TLSv1.1', 'TLSv1.2'],
            }
        ),
        CFOriginsConfig(
            domain_name='apigw1',
            origin_id='apigw1',
            origin_path='/amz_deploy',
            custom_headers=[],
            origin_policy={
                'is_s3': False,
                'origin_protocol_policy': 'https-only',
                'http_port': 80,
                'https_port': 443,
                'origin_ssl_protocols': ['TLSv1', 'TLSv1.1', 'TLSv1.2'],
            }
        )
    ]

    cache_behavior = [
        CFCacheBehaviorConfig(
            is_default=True,
            path_pattern='',
            allowed_methods=['GET', 'HEAD'],
            cached_methods=['GET', 'HEAD'],
            target_origin_id='app2',
            forward_cookies='all',
            forwarded_headers=[],
            viewer_protocol_policy='allow-all',
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
            trusted_signers=[],
            query_string=True
        ),
        CFCacheBehaviorConfig(
            is_default=False,
            path_pattern='/login',
            allowed_methods=['GET', 'POST', 'HEAD', 'DELETE', 'OPTIONS', 'PATCH', 'PUT'],
            cached_methods=['GET', 'HEAD'],
            target_origin_id='apigw1',
            forward_cookies='all',
            forwarded_headers=['Accept',
                               'Accept-Charset',
                               'Accept-Datetime',
                               'Accept-Language',
                               'Authorization',
                               'Content-Type',
                               'Origin',
                               'Referer',
                               'Set-Cookie'],
            viewer_protocol_policy='https-only',
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
            trusted_signers=[],
            query_string=False
        ),
    ]

    distribution_config = CFDistributionConfig(
        aliases=[],
        comment='SysTestCFDistribution',
        default_root_object='',
        enabled=True,
        price_class='PriceClass_All',
        error_page_path='',
        acm_cert_arn=None,
        minimum_protocol_version='TLSv1',
        ssl_support_method='sni-only'
    )

    CFDistributionLeaf(leaf_title='cfdist',
                       tree_name='tree',
                       template=template,
                       cf_origins_config=origins,
                       cf_cache_behavior_config=cache_behavior,
                       cf_distribution_config=distribution_config)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
