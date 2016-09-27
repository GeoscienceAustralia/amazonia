#!/usr/bin/python3

from amazonia.classes.amz_zd_autoscaling import ZdAutoscalingUnit
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
from network_setup import get_network_config


def main():
    userdata = """
#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - httpd

runcmd:
 - service httpd start
    """
    network_config, template = get_network_config()

    elb_health_check = 'TCP:80'
    healthy_threshold = 10
    unhealthy_threshold = 2
    interval = 300
    timeout = 30
    minsize = 1
    maxsize = 1
    health_check_grace_period = 300
    health_check_type = 'ELB'

    image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='JSESSION'
        ),
        ElbListenersConfig(
            instance_port='8080',
            loadbalancer_port='8080',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='SESSIONTOKEN'
        )
    ]

    block_devices_config = [BlockDevicesConfig(device_name='/dev/xvda',
                                               ebs_volume_size='15',
                                               ebs_volume_type='gp2',
                                               ebs_encrypted=False,
                                               ebs_snapshot_id=None,
                                               virtual_name=False)]

    elb_config = ElbConfig(elb_listeners_config=elb_listeners_config,
                           elb_log_bucket=None,
                           elb_health_check=elb_health_check,
                           public_unit=True,
                           ssl_certificate_id=None,
                           healthy_threshold=healthy_threshold,
                           unhealthy_threshold=unhealthy_threshold,
                           interval=interval,
                           timeout=timeout
                           )
    blue_asg_config = AsgConfig(health_check_grace_period=health_check_grace_period,
                                health_check_type=health_check_type,
                                minsize=minsize,
                                maxsize=maxsize,
                                image_id=image_id,
                                instance_type=instance_type,
                                userdata=userdata,
                                iam_instance_profile_arn=None,
                                block_devices_config=block_devices_config,
                                simple_scaling_policy_config=None)
    green_asg_config = AsgConfig(health_check_grace_period=health_check_grace_period,
                                 health_check_type=health_check_type,
                                 minsize=minsize,
                                 maxsize=maxsize,
                                 image_id=image_id,
                                 instance_type=instance_type,
                                 userdata=userdata,
                                 iam_instance_profile_arn=None,
                                 block_devices_config=block_devices_config,
                                 simple_scaling_policy_config=None)
    ZdAutoscalingUnit(
        unit_title='app1',
        template=template,
        dependencies=['app2:80'],
        stack_config=network_config,
        elb_config=elb_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )
    ZdAutoscalingUnit(
        unit_title='app2',
        template=template,
        dependencies=['app1:80'],
        stack_config=network_config,
        elb_config=elb_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
