#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.asg import Asg
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from network_setup import get_network_config


def main():
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

    block_devices_config = [
        BlockDevicesConfig(device_name='/dev/xvda',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=False,
                           ebs_snapshot_id=None,
                           virtual_name=False),
        BlockDevicesConfig(device_name='/dev/xvda2',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=False,
                           ebs_snapshot_id='ami-ce0531ad',
                           virtual_name=False),
        BlockDevicesConfig(device_name='/dev/sda1',
                           ebs_volume_size=None,
                           ebs_volume_type=None,
                           ebs_encrypted=False,
                           ebs_snapshot_id=None,
                           virtual_name=True),
        BlockDevicesConfig(device_name='/dev/sda2',
                           ebs_volume_size='15',
                           ebs_volume_type='gp2',
                           ebs_encrypted=True,
                           ebs_snapshot_id=None,
                           virtual_name=False)
    ]

    asg_config = AsgConfig(
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        minsize=1,
        maxsize=2,
        userdata='',
        health_check_grace_period=300,
        health_check_type='ELB',
        iam_instance_profile_arn='arn:aws:iam::12345678987654321:role/InstanceProfileRole',
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None,
        ec2_scheduled_shutdown=None,
        pausetime='10',
        owner='ga.autobots@gmail.com'
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
