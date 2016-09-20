#!/usr/bin/python3

from amazonia.classes.cf_cache_behavior_config import CFCacheBehavior
from amazonia.classes.cf_distribution_config import CFDistributionConfig
from amazonia.classes.cf_distribution_unit import CloudfrontConfigError
from amazonia.classes.cf_origins_config import CFOriginsConfig
from nose.tools import *


def create_cf_distribution_config(aliases=('wwwelb.ap-southeast-2.elb.amazonaws.com'),
                                  comment='UnitTestCFDistConfig',
                                  default_root_object='index.html',
                                  enabled=True, price_class='PriceClass_All',
                                  error_page_path='index.html',
                                  acm_cert_arn='arn.acm.certificate',
                                  minimum_protocol_version='TLSv1',
                                  ssl_support_method='sni-only'):
    """
    Create a CFDistributionConfig object
    :param aliases: A list of DNS CNAME aliases
    :param comment: A description for the distribution
    :param default_root_object: The object (e.g. index.html) that should be provided when the root URL is requested
    :param enabled: Controls whether the distribution is enabled to access user requests
    :param price_class: The price class that corresponds with the maximum price to be paid for the service
    :param error_page_path: The error page that should be served when an HTTP error code is returned
    :param acm_cert_arn: ARN of the ACM certificate
    :param minimum_protocol_version: The minimum version of the SSL protocol that should be used for HTTPS
    :param ssl_support_method: Specifies how Cloudfront serves HTTPS requests
    :return: Instance of CFDistributionConfig
    """
    cf_distribution_config = CFDistributionConfig(
        aliases=aliases,
        comment=comment,
        default_root_object=default_root_object,
        enabled=enabled,
        price_class=price_class,
        error_page_path=error_page_path,
        acm_cert_arn=acm_cert_arn,
        minimum_protocol_version=minimum_protocol_version,
        ssl_support_method=ssl_support_method
    )

    return cf_distribution_config


def create_s3_origin(domain_name='amazonia-elb-bucket.s3.amazonaws.com', origin_id='S3-bucket-id',
                     is_s3=True, origin_access_identity='originaccessid1'):
    """
    Create an S3Origin object
    :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
    :param origin_id: An identifier for this origin (must be unique within this distribution)
    :param is_s3: Boolean value indicating whether the object is an S3Origin or a CustomOrigin
    :param origin_access_identity: The Cloudfront origin access identity to associate with the origin
    :return: Instance of S3Origin object
    """

    origin = CFOriginsConfig(
        domain_name=domain_name,
        origin_id=origin_id,
        origin_path='',
        custom_headers={
            'Origin':'http://www.domain.com',
            'Accept':'True'
        },
        origin_policy={
            'is_s3': is_s3,
            'origin_access_identity': origin_access_identity
        }
    )

    return origin


def create_custom_origin(domain_name='amazonia-elb-bucket.s3.amazonaws.com',
                         origin_id='S3-bucket-id',
                         is_s3=False,
                         origin_protocol_policy='https-only',
                         http_port='80',
                         https_port='443',
                         origin_ssl_protocols=('TLSv1', 'TLSv1.1', 'TLSv1.2')):
    """
    Create a CustomOrigin object
    :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
    :param origin_id: An identifier for this origin (must be unique within this distribution)
    :param is_s3: Boolean value indicating whether the object is an S3Origin or a CustomOrigin
    :param origin_protocol_policy: Which protocols the origin listens on (http, https, both)
    :param http_port: The HTTP port the origin listens on
    :param https_port: The HTTPS port the origin listens on
    :param origin_ssl_protocols: The SSL protocols to be used when establishing an HTTPS connection with the origin
    :return: Instance of CustomOrigin object
    """

    origin = CFOriginsConfig(
        domain_name=domain_name,
        origin_id=origin_id,
        origin_path='/path',
        custom_headers={},
        origin_policy={
            'is_s3': is_s3,
            'origin_protocol_policy': origin_protocol_policy,
            'http_port': http_port,
            'https_port': https_port,
            'origin_ssl_protocols': origin_ssl_protocols,
        }
    )

    return origin


def create_cache_behavior(is_default=False,
                          path_pattern='/index.html',
                          allowed_methods=('GET', 'POST'),
                          cached_methods=('GET', 'POST'),
                          target_origin_id='S3-bucket-id',
                          forward_cookies='all',
                          forwarded_headers=('Accept', 'Set-Cookie'),
                          viewer_protocol_policy='allow-all',
                          min_ttl=0,
                          default_ttl=0,
                          max_ttl=0,
                          trusted_signers=('self'),
                          query_string=True):
    """
    :param path_pattern: The pattern to which this cache behavior applies
    :param allowed_methods: List of HTTP methods that can be passed to the origin
    :param cached_methods: List of HTTP methods for which Cloudfront caches responses
    :param target_origin_id: Value of the unique ID for the default cache behavior of this distribution
    :param viewer_protocol_policy: The protocol that users can use to access origin files
    :param min_ttl: The minimum amount of time objects should stay in the cache
    :param default_ttl: The default amount of time objects stay in the cache
    :param max_ttl: The maximum amount of time objects should stay in the cache
    :param forward_cookies: boolean to forward cookies to origin
    :param trusted_signers: list of identifies that are trusted to sign cookies on behalf of this behavior
    :param query_string: indicates whether to forward query strings to the origin
    :return: Instance of CacheBehavior object
    """
    cache_behavior = CFCacheBehavior(
        is_default=is_default,
        path_pattern=path_pattern,
        allowed_methods=allowed_methods,
        cached_methods=cached_methods,
        target_origin_id=target_origin_id,
        forward_cookies=forward_cookies,
        forwarded_headers=forwarded_headers,
        viewer_protocol_policy=viewer_protocol_policy,
        min_ttl=min_ttl,
        default_ttl=default_ttl,
        max_ttl=max_ttl,
        trusted_signers=trusted_signers,
        query_string=query_string
    )

    return cache_behavior


def test_s3_origin():
    """
    Test to check S3Origin object inputs match the created outputs
    """

    domain_name = 'www.domain.com'
    is_s3 = True
    origin_access_identity = 'origin-access-identity/cloudfront/TestOAI'

    helper_cf_origin = create_s3_origin(domain_name=domain_name,
                                        is_s3=is_s3,
                                        origin_access_identity=origin_access_identity
                                        )

    assert_equal(domain_name, helper_cf_origin.domain_name)
    assert_equal(is_s3, helper_cf_origin.origin_policy['is_s3'])
    assert_equal(origin_access_identity, helper_cf_origin.origin_access_identity)


def test_s3_origin_oai():
    """
    Test to check S3Origin object inputs match the created outputs
    """

    domain_name = 'www.domain.com'
    is_s3 = True
    origin_access_identity = 'TestOAI'

    helper_cf_origin = create_s3_origin(domain_name=domain_name,
                                        is_s3=is_s3,
                                        origin_access_identity=origin_access_identity
                                        )

    assert_equal(domain_name, helper_cf_origin.domain_name)
    assert_equal(is_s3, helper_cf_origin.origin_policy['is_s3'])
    assert_equal(origin_access_identity, helper_cf_origin.origin_access_identity)


def test_custom_origin():
    """
    Test to check CustomOrigin object inputs match the created outputs
    """

    domain_name = 'www.domain.com'
    is_s3 = False
    origin_protocol_policy = 'https-only'
    http_port = '80'
    https_port = '443'
    origin_ssl_protocols = ('TLSv1', 'TLSv1.1', 'TLSv1.2')

    helper_cf_origin = create_custom_origin(domain_name=domain_name,
                                            is_s3=is_s3,
                                            origin_protocol_policy=origin_protocol_policy,
                                            http_port=http_port,
                                            https_port=https_port,
                                            origin_ssl_protocols=origin_ssl_protocols
                                            )

    assert_equal(domain_name, helper_cf_origin.domain_name)
    assert_equal(is_s3, helper_cf_origin.origin_policy['is_s3'])
    assert_equal(origin_protocol_policy, helper_cf_origin.origin_protocol_policy)
    assert_equal(http_port, helper_cf_origin.http_port)
    assert_equal(https_port, helper_cf_origin.https_port)
    assert_equal(origin_ssl_protocols, helper_cf_origin.origin_ssl_protocols)


def test_cf_cache_behavior():
    """
    Test to check CacheBehavior object inputs match the created outputs
    """
    is_default=False
    path_pattern = '/index.html'
    allowed_methods = ('GET', 'POST')
    cached_methods = ('GET', 'POST'),
    target_origin_id = 'S3-bucket-id'
    forward_cookies = 'all'
    forwarded_headers = ('Accept', 'Set-Cookie')
    viewer_protocol_policy = 'allow-all'
    min_ttl = 0
    default_ttl = 0
    max_ttl = 0
    trusted_signers = ('self')
    query_string = True

    helper_cf_cache_behavior = create_cache_behavior(is_default=is_default,
                                                     path_pattern=path_pattern,
                                                     allowed_methods=allowed_methods,
                                                     cached_methods=cached_methods,
                                                     target_origin_id=target_origin_id,
                                                     forward_cookies=forward_cookies,
                                                     forwarded_headers=forwarded_headers,
                                                     viewer_protocol_policy=viewer_protocol_policy,
                                                     min_ttl=min_ttl,
                                                     default_ttl=default_ttl,
                                                     max_ttl=max_ttl,
                                                     trusted_signers=trusted_signers,
                                                     query_string=query_string)

    assert_equal(is_default, helper_cf_cache_behavior.is_default)
    assert_equal(path_pattern, helper_cf_cache_behavior.path_pattern)
    assert_equal(allowed_methods, helper_cf_cache_behavior.allowed_methods)
    assert_equal(cached_methods, helper_cf_cache_behavior.cached_methods)
    assert_equal(target_origin_id, helper_cf_cache_behavior.target_origin_id)
    assert_equal(forward_cookies, helper_cf_cache_behavior.forward_cookies)
    assert_equal(forwarded_headers, helper_cf_cache_behavior.forwarded_headers)
    assert_equal(min_ttl, helper_cf_cache_behavior.min_ttl)
    assert_equal(default_ttl, helper_cf_cache_behavior.default_ttl)
    assert_equal(max_ttl, helper_cf_cache_behavior.max_ttl)
    assert_equal(trusted_signers, helper_cf_cache_behavior.trusted_signers)
    assert_equal(query_string, helper_cf_cache_behavior.query_string)


def test_cf_distribution_config():
    """
    Test to check DistributionConfig object inputs match the created outputs
    """

    aliases = 'wwwelb.ap-southeast-2.elb.amazonaws.com'
    comment = 'UnitTestCFDistConfig'
    default_root_object = 'index.html'
    enabled = True
    price_class = 'PriceClass_All'
    error_page_path = 'index.html'
    acm_cert_arn = 'arn:aws:cloudfront::123456789012:distribution/ABCD1234EFGH56'
    minimum_protocol_version = 'TLSv1'
    ssl_support_method = 'sni-only'

    origins = []
    cache_behaviors = []

    helper_cf_dist = create_cf_distribution_config(aliases=aliases,
                                                   comment=comment,
                                                   default_root_object=default_root_object,
                                                   enabled=enabled,
                                                   price_class=price_class,
                                                   error_page_path=error_page_path,
                                                   acm_cert_arn=acm_cert_arn,
                                                   minimum_protocol_version=minimum_protocol_version,
                                                   ssl_support_method=ssl_support_method)

    assert_equal(aliases, helper_cf_dist.aliases)
    assert_equal(comment, helper_cf_dist.comment)
    assert_equal(default_root_object, helper_cf_dist.default_root_object)
    assert_equal(enabled, helper_cf_dist.enabled)
    assert_equal(price_class, helper_cf_dist.price_class)
    assert_equal(acm_cert_arn, helper_cf_dist.acm_cert_arn)
    assert_equal(error_page_path, helper_cf_dist.error_page_path)