from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.cf_cache_behavior_config import CFCacheBehavior
from amazonia.classes.cf_distribution_config import CFDistributionConfig
from amazonia.classes.cf_origins_config import CFOriginsConfig
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.simple_scaling_policy_config import SimpleScalingPolicyConfig
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig, ApiGatewayDeploymentConfig
from amazonia.classes.api_gateway_config import ApiGatewayRequestConfig, ApiGatewayResponseConfig
from amazonia.classes.lambda_config import LambdaConfig


class ComplexObjectFieldMapping(object):
    def __init__(self, constructor, is_list, key_list):
        """
        Simple class to hold mapping information between input data and config classes
        :param constructor: config class definition
        :param is_list: is the field a list of config objects or a single config object?
        :param key_list: expected config keys
        """
        self.constructor = constructor
        self.is_list = is_list
        self.key_list = key_list


class YamlFields(object):
    """Simple object to consolidate a number of key list constants"""

    # elb_config field list
    elb_config_key_list = ['instance_protocol',
                           'loadbalancer_protocol',
                           'instance_port',
                           'loadbalancer_port',
                           'elb_health_check',
                           'public_unit',
                           'elb_log_bucket',
                           'ssl_certificate_id',
                           'healthy_threshold',
                           'unhealthy_threshold',
                           'interval',
                           'timeout',
                           'sticky_app_cookies'
                           ]

    # asg_config field list
    asg_config_key_list = ['sns_topic_arn',
                           'sns_notification_types',
                           'health_check_grace_period',
                           'health_check_type',
                           'minsize',
                           'maxsize',
                           'image_id',
                           'instance_type',
                           'userdata',
                           'iam_instance_profile_arn',
                           'block_devices_config',
                           'simple_scaling_policy_config'
                           ]

    # simple_scaling_policy field list
    simple_scaling_policy_config_key_list = ['name',
                                             'description',
                                             'metric_name',
                                             'comparison_operator',
                                             'threshold',
                                             'evaluation_periods',
                                             'period',
                                             'scaling_adjustment',
                                             'cooldown']

    # block_devices_config field list
    block_devices_config_key_list = ['device_name',
                                     'ebs_volume_size',
                                     'ebs_volume_type',
                                     'ebs_encrypted',
                                     'ebs_snapshot_id',
                                     'virtual_name',
                                     ]

    # cloudfront distribution config key list
    cf_distribution_config_key_list = [
        'aliases',
        'comment',
        'default_root_object',
        'enabled',
        'price_class',
        'error_page_path',
        'acm_cert_arn',
        'minimum_protocol_version',
        'ssl_support_method'
    ]

    # api_method_config field list
    api_method_config = [
        'method_name',
        'lambda_unit',
        'httpmethod',
        'authorizationtype',
        'request_config',
        'response_config'
    ]

    # api_request_config field list
    api_request_config = [
        'templates',
        'parameters'
    ]

    # api_response_config field list
    api_response_config = [
        'templates',
        'parameters',
        'selectionpattern',
        'statuscode',
        'models'
    ]

    # api_stage_config field list
    api_deployment_config = [
        'apiname',
        'stagename'
    ]

    # cloudfront origins config key list
    cf_origins_config_key_list = [
        'domain_name',
        'origin_id',
        'origin_path',
        'custom_headers',
        'origin_policy'
    ]

    # cloudfront cache behavior config key list
    cf_cache_behavior_config_key_list = [
        'is_default',
        'path_pattern',
        'allowed_methods',
        'cached_methods',
        'target_origin_id',
        'forward_cookies',
        'forwarded_headers',
        'viewer_protocol_policy',
        'min_ttl',
        'default_ttl',
        'max_ttl',
        'trusted_signers',
        'query_string'
    ]

    # database_config field list
    database_config_key_list = [
        'db_name',
        'db_instance_type',
        'db_engine',
        'db_port',
        'db_hdd_size',
        'db_snapshot_id',
        'db_backup_window',
        'db_backup_retention',
        'db_maintenance_window',
        'db_storage_type'
    ]

    # stack parameter field list
    stack_key_list = [
        'code_deploy_service_role',
        'keypair',
        'availability_zones',
        'vpc_cidr',
        'public_cidr',
        'jump_image_id',
        'jump_instance_type',
        'nat_image_id',
        'nat_instance_type',
        'nat_highly_available',
        'home_cidrs',
        'public_hosted_zone_name',
        'private_hosted_zone_name',
        'cf_distribution_units',
        'zd_autoscaling_units',
        'autoscaling_units',
        'api_gateway_units',
        'lambda_units',
        'database_units',
        'iam_instance_profile_arn',
        'owner_emails',
        'nat_alerting'
    ]

    # autoscaling unit parameter field list
    autoscaling_unit_key_list = [
        'unit_title',
        'dependencies',
        'elb_config',
        'asg_config'
    ]

    # database unit parameter field list
    database_unit_key_list = [
        'unit_title',
        'database_config'
    ]

    # cloudfront distribution unit parameter field list
    cf_distribution_unit_key_list = [
        'unit_title',
        'cf_cache_behavior_config',
        'cf_origins_config',
        'cf_distribution_config'
    ]

    # zd autoscaling unit parameter field list
    zd_autoscaling_unit_key_list = [
        'unit_title',
        'dependencies',
        'elb_config',
        'blue_asg_config',
        'green_asg_config'
    ]

    # api parameter field list
    api_gateway_unit_key_list = [
        'unit_title',
        'method_config',
        'deployment_config'
    ]

    # lambda unit parameter field list
    lambda_unit_key_list = [
        'unit_title',
        'dependencies',
        'lambda_config'
    ]

    # lambda config field list
    lambda_config_key_list = [
        'lambda_s3_bucket',
        'lambda_s3_key',
        'lambda_description',
        'lambda_function_name',
        'lambda_handler',
        'lambda_memory_size',
        'lambda_role_arn',
        'lambda_runtime',
        'lambda_timeout',
        'lambda_schedule'
    ]

    # config classes
    complex_object_field_mapping = {
        'elb_config':
            ComplexObjectFieldMapping(ElbConfig, False, elb_config_key_list),
        'asg_config':
            ComplexObjectFieldMapping(AsgConfig, False, asg_config_key_list),
        'blue_asg_config':
            ComplexObjectFieldMapping(AsgConfig, False, asg_config_key_list),
        'green_asg_config':
            ComplexObjectFieldMapping(AsgConfig, False, asg_config_key_list),
        'database_config':
            ComplexObjectFieldMapping(DatabaseConfig, False, database_config_key_list),
        'block_devices_config':
            ComplexObjectFieldMapping(BlockDevicesConfig, True, block_devices_config_key_list),
        'simple_scaling_policy_config':
            ComplexObjectFieldMapping(SimpleScalingPolicyConfig, True, simple_scaling_policy_config_key_list),
        'autoscaling_units':
            ComplexObjectFieldMapping(dict, True, autoscaling_unit_key_list),
        'zd_autoscaling_units':
            ComplexObjectFieldMapping(dict, True, zd_autoscaling_unit_key_list),
        'database_units':
            ComplexObjectFieldMapping(dict, True, database_unit_key_list),
        'cf_distribution_units':
            ComplexObjectFieldMapping(dict, True, cf_distribution_unit_key_list),
        'cf_cache_behavior_config':
            ComplexObjectFieldMapping(CFCacheBehavior, True, cf_cache_behavior_config_key_list),
        'cf_distribution_config':
            ComplexObjectFieldMapping(CFDistributionConfig, False, cf_distribution_config_key_list),
        'cf_origins_config':
            ComplexObjectFieldMapping(CFOriginsConfig, True, cf_origins_config_key_list),
        'api_gateway_units':
            ComplexObjectFieldMapping(dict, True, api_gateway_unit_key_list),
        'method_config':
            ComplexObjectFieldMapping(ApiGatewayMethodConfig, True, api_method_config),
        'request_config':
            ComplexObjectFieldMapping(ApiGatewayRequestConfig, False, api_request_config),
        'response_config':
            ComplexObjectFieldMapping(ApiGatewayResponseConfig, True, api_response_config),
        'deployment_config':
            ComplexObjectFieldMapping(ApiGatewayDeploymentConfig, True, api_deployment_config),
        'lambda_units':
            ComplexObjectFieldMapping(dict, True, lambda_unit_key_list),
        'lambda_config':
            ComplexObjectFieldMapping(LambdaConfig, False, lambda_config_key_list),
    }

