#!/usr/bin/python3

from amazonia.classes.amz_api_gateway import ApiGatewayUnit
from amazonia.classes.amz_autoscaling import AutoscalingUnit
from amazonia.classes.amz_cf_distribution import CFDistributionUnit
from amazonia.classes.amz_lambda import LambdaUnit
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.cf_distribution_config import CFDistributionConfig, CFOriginsConfig, CFCacheBehaviorConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.elb_config import ElbListenersConfig
from amazonia.classes.lambda_config import LambdaConfig
from network_setup import get_network_config


def main():
    network_config, template = get_network_config()

    userdata = """
    #cloud-config
    repo_update: true
    repo_upgrade: all

    packages:
     - httpd

    runcmd:
     - service httpd start
        """
    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie=None
        )
    ]

    elb_config = ElbConfig(
        elb_health_check='TCP:80',
        elb_log_bucket=None,
        public_unit=True,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        elb_listeners_config=elb_listeners_config
    )

    block_devices_config = [BlockDevicesConfig(device_name='/dev/xvda',
                                               ebs_volume_size='15',
                                               ebs_volume_type='gp2',
                                               ebs_encrypted=False,
                                               ebs_snapshot_id=None,
                                               virtual_name=False)
                            ]

    asg_config = AsgConfig(
        minsize=1,
        maxsize=2,
        health_check_grace_period=300,
        health_check_type='ELB',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        userdata=userdata,
        iam_instance_profile_arn=None,
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None,
        ec2_scheduled_shutdown=None,
        pausetime='10',
        owner='autobots'
    )

    app_name = 'app1'

    AutoscalingUnit(
        unit_title=app_name,
        template=template,
        dependencies=[],
        stack_config=network_config,
        elb_config=elb_config,
        asg_config=asg_config,
        ec2_scheduled_shutdown=None
    )

    apiname = 'apigw1'
    methodname = 'login'
    lambda_title = 'MyLambda'
    httpmethod = 'POST'
    authorizationtype = 'NONE'

    request_template = {'application/json': """{ "username": $input.json('$.username')}"""}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-COokie': 'integration.response.body.TESTVALUE'}
    response_models = {'application/json': 'Empty'}
    statuscode = '200'
    selectionpattern = ''
    request_config = ApiGatewayRequestConfig(templates=request_template,
                                             parameters=request_parameters)
    response_config1 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=statuscode,
                                                models=response_models,
                                                selectionpattern=selectionpattern)
    statuscode = '403'
    selectionpattern = 'Invalid.*'
    response_config2 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=statuscode,
                                                models=response_models,
                                                selectionpattern=selectionpattern)

    method_config = ApiGatewayMethodConfig(method_name=methodname,
                                           lambda_unit=lambda_title,
                                           request_config=request_config,
                                           response_config=[response_config1, response_config2],
                                           httpmethod=httpmethod,
                                           authorizationtype=authorizationtype)
    lambda_config = LambdaConfig(
        lambda_s3_bucket='smallest-bucket-in-history',
        lambda_s3_key='test_lambda.zip',
        lambda_description='test function',
        lambda_function_name='test_lambda',
        lambda_handler='test_lambda.lambda_handler',
        lambda_memory_size=128,
        lambda_role_arn='arn:aws:iam::123456789:role/lambda_basic_vpc_execution_with_s3',
        lambda_runtime='python2.7',
        lambda_timeout=1,
        lambda_schedule='rate(5 minutes)'
    )

    LambdaUnit(
        unit_title=lambda_title,
        template=template,
        dependencies=[],
        stack_config=network_config,
        lambda_config=lambda_config
    )

    ApiGatewayUnit(unit_title=apiname,
                   template=template,
                   method_config=[method_config],
                   stack_config=network_config)

    origins = [
        CFOriginsConfig(
            domain_name=app_name,
            origin_id=app_name,
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
            domain_name=apiname,
            origin_id=apiname,
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
            target_origin_id='app1',
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

    CFDistributionUnit(unit_title='cfdist',
                       template=template,
                       stack_config=network_config,
                       cf_origins_config=origins,
                       cf_cache_behavior_config=cache_behavior,
                       cf_distribution_config=distribution_config)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
