#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.asg import Asg
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.simple_scaling_policy_config import SimpleScalingPolicyConfig
from network_setup import get_network_config
from troposphere import Template


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

    load_balancer = template.add_resource(elb.LoadBalancer('MyELB',
                                                           CrossZone=True,
                                                           HealthCheck=elb.HealthCheck(
                                                               Target='HTTP:8080/error/noindex.html',
                                                               HealthyThreshold='2',
                                                               UnhealthyThreshold='5',
                                                               Interval='15',
                                                               Timeout='5'),
                                                           Listeners=[elb.Listener(LoadBalancerPort='80',
                                                                                   Protocol='HTTP',
                                                                                   InstancePort='80',
                                                                                   InstanceProtocol='HTTP')],
                                                           Scheme='internet-facing',
                                                           Subnets=network_config.public_subnets))

    block_devices_config = [BlockDevicesConfig(device_name='/dev/xvda',
                                               ebs_volume_size='15',
                                               ebs_volume_type='gp2',
                                               ebs_encrypted=False,
                                               ebs_snapshot_id=None,
                                               virtual_name=False)]

    simple_scaling_policy_config = [
        SimpleScalingPolicyConfig(name='heavy - load',
                                  description='When under heavy CPU load for five minutes, add two instances, '
                                              'wait 45 seconds',
                                  metric_name='CPUUtilization',
                                  comparison_operator='GreaterThanThreshold',
                                  threshold='45',
                                  evaluation_periods=1,
                                  period=300,
                                  scaling_adjustment=1,
                                  cooldown=45),
        SimpleScalingPolicyConfig(name='light - load',
                                  description='When under light CPU load for 6 consecutive periods of five minutes,'
                                              ' remove one instance, wait 120 seconds',
                                  metric_name='CPUUtilization',
                                  comparison_operator='LessThanOrEqualToThreshold',
                                  threshold='15',
                                  evaluation_periods=6,
                                  period=300,
                                  scaling_adjustment=-1,
                                  cooldown=120),
        SimpleScalingPolicyConfig(name='medium - load',
                                  description='When under medium CPU load for five minutes, add one instance, '
                                              'wait 45 seconds',
                                  metric_name='CPUUtilization',
                                  comparison_operator='GreaterThanOrEqualToThreshold',
                                  threshold='25',
                                  evaluation_periods=1,
                                  period=300,
                                  scaling_adjustment=1,
                                  cooldown=120)
    ]

    asg_config = AsgConfig(
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        minsize=1,
        maxsize=2,
        userdata=userdata,
        health_check_grace_period=300,
        health_check_type='ELB',
        iam_instance_profile_arn='arn:aws:iam::12345678987654321:role/InstanceProfileRole',
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=simple_scaling_policy_config,
        ec2_scheduled_shutdown=None,
        pausetime='10'
    )

    Asg(title='simple',
        network_config=network_config,
        load_balancers=[load_balancer],
        template=template,
        asg_config=asg_config
        )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
