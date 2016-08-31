#!/usr/bin/python3

from nose.tools import *
from amazonia.classes.cf_distribution_unit import CFDistributionUnit
from amazonia.classes.cf_distribution_config import CFDistributionConfig
from amazonia.classes.cf_origins_config import CFOriginsConfig
from amazonia.classes.cf_cache_behaviors_config import CFCacheBehaviors
from troposphere import Template, cloudfront

def create_cf_distribution_config(aliases=('wwwelb.ap-southeast-2.elb.amazonaws.com'),
                                 comment='UnitTestCFDistConfig', default_root_object='index.html',
                                 enabled=True, price_class='PriceClass_All', target_origin_id='originId',
                                 allowed_methods=('GET','HEAD'), cached_methods=('GET','HEAD'),
                                 trusted_signers=('self'), viewer_protocol_policy='https-only',
                                 min_ttl=0, default_ttl=0, max_ttl=0, error_page_path='index.html'):
    """
    Create a CFDistributionConfig object
    :param aliases: A list of DNS CNAME aliases
    :param comment: A description for the distribution
    :param default_root_object: The object (e.g. index.html) that should be provided when the root URL is requested
    :param enabled: Controls whether the distribution is enabled to access user requests
    :param price_class: The price class that corresponds with the maximum price to be paid for the service
    :param target_origin_id: Value of the unique ID for the default cache behavior of this distribution
    :param allowed_methods: List of HTTP methods that can be passed to the origin
    :param cached_methods: List of HTTP methods for which Cloudfront caches responses
    :param trusted_signers: List of AWS accounts that can create signed URLs in order to access private content
    :param viewer_protocol_policy: The protocol that users can use to access origin files
    :param min_ttl: The minimum amount of time objects should stay in the cache
    :param default_ttl: The default amount of time objects stay in the cache
    :param max_ttl: The maximum amount of time objects should stay in the cache
    :param error_page_path: The error page that should be served when an HTTP error code is returned
    :return: Instance of CFDistributionConfig
    """
    cf_distribution_config = CFDistributionConfig(
        aliases=aliases,
        comment=comment,
        default_root_object=default_root_object,
        enabled=enabled,
        price_class=price_class,
        target_origin_id=target_origin_id,
        allowed_methods=allowed_methods,
        cached_methods=cached_methods,
        trusted_signers=trusted_signers,
        viewer_protocol_policy=viewer_protocol_policy,
        min_ttl=min_ttl,
        default_ttl=default_ttl,
        max_ttl=max_ttl,
        error_page_path=error_page_path,
    )

    return cf_distribution_config

def create_s3_origin(domain_name='amazonia-elb-bucket.s3.amazonaws.com', origin_id='S3-bucket-id',
                   is_s3=True, origin_access_identity = 'originaccessid1'):
    """
    Create an S3Origin object
    :param domain_name: The DNS name of the S3 bucket or HTTP server which this distribution will point to
    :param origin_id: An identifier for this origin (must be unique within this distribution)
    :param is_s3: Boolean value indicating whether the object is an S3Origin or a CustomOrigin
    :param origin_access_identity: The Cloudfront origin access identity to associate with the origin
    :return: Instance of S3Origin object
    """
    template = Template()

    origin = CFOriginsConfig(
        template=template,
        domain_name=domain_name,
        origin_id=origin_id,
        origin_policy={
            'is_s3': is_s3,
            'origin_access_identity': origin_access_identity
        }
    )

    return origin


def create_custom_origin(domain_name='amazonia-elb-bucket.s3.amazonaws.com', origin_id='S3-bucket-id',
                        is_s3=False, origin_protocol_policy='https-only', http_port='80', https_port='443',
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
    template = Template()

    origin = CFOriginsConfig(
        template=template,
        domain_name=domain_name,
        origin_id=origin_id,
        origin_policy={
            'is_s3': is_s3,
            'origin_protocol_policy': origin_protocol_policy,
            'http_port': http_port,
            'https_port': https_port,
            'origin_ssl_protocols': origin_ssl_protocols,
        }
    )

    return origin

def create_cache_behavior(path_pattern='/index.html', allowed_methods=('GET', 'POST'), cached_methods=('GET', 'POST'),
        target_origin_id='S3-bucket-id', forward_cookies='all', viewer_protocol_policy='allow-all',
        min_ttl=0, default_ttl=0, max_ttl=0, trusted_signers=('self')):
    """
    :param path_pattern: The pattern to which this cache behavior applies
    :param allowed_methods: List of HTTP methods that can be passed to the origin
    :param cached_methods: List of HTTP methods for which Cloudfront caches responses
    :param target_origin_id: Value of the unique ID for the default cache behavior of this distribution
    :param viewer_protocol_policy: The protocol that users can use to access origin files
    :param min_ttl: The minimum amount of time objects should stay in the cache
    :param default_ttl: The default amount of time objects stay in the cache
    :param max_ttl: The maximum amount of time objects should stay in the cache
    :return: Instance of CacheBehavior object
    """
    cache_behavior = CFCacheBehaviors(
        path_pattern=path_pattern,
        allowed_methods=allowed_methods,
        cached_methods=cached_methods,
        target_origin_id=target_origin_id,
        forward_cookies=forward_cookies,
        viewer_protocol_policy=viewer_protocol_policy,
        min_ttl=min_ttl,
        default_ttl=default_ttl,
        max_ttl=max_ttl,
        trusted_signers=trusted_signers
    )

    return cache_behavior

def test_s3_origin():
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
    assert_equal(origin_access_identity, helper_cf_origin.origin_policy['origin_access_identity'])

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
    path_pattern = '/index.html'
    allowed_methods = ('GET', 'POST')
    cached_methods = ('GET', 'POST'),
    target_origin_id = 'S3-bucket-id'
    forward_cookies = 'all'
    viewer_protocol_policy = 'allow-all'
    min_ttl = 0
    default_ttl = 0
    max_ttl = 0
    trusted_signers = ('self')

    helper_cf_cache_behavior = create_cache_behavior(path_pattern=path_pattern, allowed_methods=allowed_methods,
                                        cached_methods=cached_methods, target_origin_id=target_origin_id,
                                        forward_cookies=forward_cookies,viewer_protocol_policy=viewer_protocol_policy,
                                        min_ttl=min_ttl, default_ttl=default_ttl, max_ttl=max_ttl,
                                        trusted_signers=trusted_signers)

    assert_equal(path_pattern, helper_cf_cache_behavior.path_pattern)
    assert_equal(allowed_methods, helper_cf_cache_behavior.allowed_methods)
    assert_equal(cached_methods, helper_cf_cache_behavior.cached_methods)
    assert_equal(target_origin_id, helper_cf_cache_behavior.target_origin_id)
    assert_equal(forward_cookies, helper_cf_cache_behavior.forward_cookies)
    assert_equal(min_ttl, helper_cf_cache_behavior.min_ttl)
    assert_equal(default_ttl, helper_cf_cache_behavior.default_ttl)
    assert_equal(max_ttl, helper_cf_cache_behavior.max_ttl)
    assert_equal(trusted_signers, helper_cf_cache_behavior.trusted_signers)

def test_cf_distribution_config():
    """
    Test to check DistributionConfig object inputs match the created outputs
    """
    template = Template()

    aliases = 'wwwelb.ap-southeast-2.elb.amazonaws.com'
    comment = 'UnitTestCFDistConfig'
    default_root_object = 'index.html'
    enabled = True
    price_class = 'PriceClass_All'
    target_origin_id = 'originId'
    allowed_methods = ['GET', 'HEAD']
    cached_methods = ['GET', 'HEAD']
    trusted_signers = 'self'
    viewer_protocol_policy = 'https-only'
    min_ttl = 0
    default_ttl = 0
    max_ttl = 0
    error_page_path = 'index.html'

    origins = []
    cache_behaviors = []

    helper_cf_dist = create_cf_distribution_config(aliases=aliases, comment=comment, default_root_object=default_root_object,
                                                 enabled=enabled, price_class=price_class, target_origin_id=target_origin_id,
                                                 allowed_methods=allowed_methods, cached_methods=cached_methods,
                                                 trusted_signers=trusted_signers, viewer_protocol_policy=viewer_protocol_policy,
                                                 min_ttl=min_ttl, default_ttl=default_ttl, max_ttl=max_ttl,
                                                 error_page_path=error_page_path)

    assert_equal(aliases, helper_cf_dist.aliases)
    assert_equal(comment, helper_cf_dist.comment)
    assert_equal(default_root_object, helper_cf_dist.default_root_object)
    assert_equal(enabled, helper_cf_dist.enabled)
    assert_equal(price_class, helper_cf_dist.price_class)
    assert_equal(target_origin_id, helper_cf_dist.target_origin_id)
    assert_equal(allowed_methods, helper_cf_dist.allowed_methods)
    assert_equal(cached_methods, helper_cf_dist.cached_methods)
    assert_equal(trusted_signers, helper_cf_dist.trusted_signers)
    assert_equal(viewer_protocol_policy, helper_cf_dist.viewer_protocol_policy)
    assert_equal(min_ttl, helper_cf_dist.min_ttl)
    assert_equal(default_ttl, helper_cf_dist.default_ttl)
    assert_equal(max_ttl, helper_cf_dist.max_ttl)
    assert_equal(error_page_path, helper_cf_dist.error_page_path)