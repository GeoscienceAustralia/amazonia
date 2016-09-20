#!/usr/bin/python3

from amazonia.classes.cf_cache_behavior_config import CFCacheBehavior
from amazonia.classes.cf_distribution_config import CFDistributionConfig
from amazonia.classes.cf_distribution_unit import CFDistributionUnit
from amazonia.classes.cf_origins_config import CFOriginsConfig
from troposphere import Template


def main():
    template = Template()

    origins = [
        CFOriginsConfig(
            domain_name='amazonia-elb-bucket.s3.amazonaws.com',
            origin_id='S3-amazonia-elb-bucket',
            origin_path='/directory',
            custom_headers={
                'Origin': 'http://www.domain.com',
                'Accept': 'True'
            },
            origin_policy={
                'is_s3': True,
                'origin_access_identity': 'originaccessid1'
            }
        ),
        CFOriginsConfig(
            domain_name='amazonia-myStackap-LXYP1MFWT9UC-145363293.ap-southeast-2.elb.amazonaws.com',
            origin_id='ELB-amazonia-myStackap-LXYP1MFWT9UC-145363293',
            origin_path='',
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
        CFCacheBehavior(
            is_default=True,
            path_pattern='/index.html',
            allowed_methods=['GET', 'HEAD'],
            cached_methods=['GET', 'HEAD'],
            target_origin_id='S3-bucket-id',
            forward_cookies='all',
            forwarded_headers=[],
            viewer_protocol_policy='allow-all',
            min_ttl=0,
            default_ttl=0,
            max_ttl=0,
            trusted_signers=[],
            query_string=True
        ),
        CFCacheBehavior(
            is_default=False,
            path_pattern='/login.js',
            allowed_methods=['GET', 'POST', 'HEAD', 'DELETE', 'OPTIONS', 'PATCH', 'PUT'],
            cached_methods=['GET', 'HEAD'],
            target_origin_id='www-origin',
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
            trusted_signers=['self'],
            query_string=False
        ),
    ]

    distribution_config = CFDistributionConfig(
        aliases=['www.test-stack.gadevs.ga', 'test-stack.gadevs.ga'],
        comment='SysTestCFDistribution',
        default_root_object='index.html',
        enabled=True,
        price_class='PriceClass_All',
        error_page_path='index.html',
        acm_cert_arn='arn:aws:acm:us-east-1:123456789012:certificate/12345678-abcd-efgh-1234-abcd12345678',
        minimum_protocol_version='TLSv1',
        ssl_support_method='sni-only'
    )

    CFDistributionUnit(unit_title='cfdist',
                       template=template,
                       network_config=None,
                       cf_origins_config=origins,
                       cf_cache_behavior_config=cache_behavior,
                       cf_distribution_config=distribution_config)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
