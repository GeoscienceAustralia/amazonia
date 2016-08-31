from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.simple_scaling_policy_config import SimpleScalingPolicyConfig


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
                           'unit_hosted_zone_name',
                           'ssl_certificate_id'
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
        'home_cidrs',
        'stack_hosted_zone_name',
        'zd_autoscaling_units',
        'autoscaling_units',
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

    # zd autoscaling unit parameter field list
    zd_autoscaling_unit_key_list = [
        'unit_title',
        'dependencies',
        'elb_config',
        'blue_asg_config',
        'green_asg_config'
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
            ComplexObjectFieldMapping(dict, True, database_unit_key_list)
    }
