#!/usr/bin/python3

from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.amz_autoscaling import AutoscalingLeaf
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
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
    template = Template()

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie=[]
        ),
        ElbListenersConfig(
            instance_port='8080',
            loadbalancer_port='8080',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='JSESSION'
        )
    ]

    elb_config = ElbConfig(
        elb_health_check='TCP:80',
        elb_log_bucket=None,
        public_unit=False,
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
        pausetime='10'
    )

    AutoscalingLeaf(
        leaf_title='app1',
        template=template,
        dependencies=['MyDb:5432'],
        elb_config=elb_config,
        asg_config=asg_config,
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        tree_name='tree',
        cd_service_role_arn=None,
        public_hosted_zone_name=None,
        keypair='INSERT_YOUR_KEYPAIR_HERE'
    )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
