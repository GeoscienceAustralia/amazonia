#!/usr/bin/python3

from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.elb_listeners_config import ElbListenersConfig
from amazonia.classes.stack import Stack


def main():
    userdata1 = """#cloud-config
repo_update: true

packages:
 - httpd

write_files:
-   content: |
        <html>
        <body>
        <h1>Amazonia created this stack!</h1>
        </body>
        </html>
    path: /var/www/html/index.html
    permissions: '0644'
    owner: root:root
runcmd:
 - service httpd start
"""
    userdata2 = """#cloud-config
repo_update: true

packages:
 - httpd

write_files:
-   content: |
        <html>
        <body>
        <h1>Amazonia created this stack too!</h1>
        </body>
        </html>
    path: /var/www/html/index.html
    permissions: '0644'
    owner: root:root
runcmd:
 - service httpd start
"""

    nat_image_id = 'ami-53371f30'
    jump_image_id = 'ami-dc361ebf'
    app_image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'
    block_devices_config = [BlockDevicesConfig(device_name='/dev/xvda',
                                               ebs_volume_size='15',
                                               ebs_volume_type='gp2',
                                               ebs_encrypted=False,
                                               ebs_snapshot_id=None,
                                               virtual_name=False)]
    elb_listeners_config = [ElbListenersConfig(loadbalancer_protocol='HTTP',
                                               instance_protocol='HTTP',
                                               instance_port='80',
                                               loadbalancer_port='80',
                                               sticky_app_cookies=[])]

    stack = Stack(
        code_deploy_service_role='arn:aws:iam::12345678987654321:role/CodeDeployServiceRole',
        keypair='pipeline',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr='10.0.0.0/16',
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_highly_available=True,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        iam_instance_profile_arn=None,
        owner_emails=[],
        home_cidrs=[{'name': 'GA', 'cidr': '123.123.12.34/32'}],
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        public_hosted_zone_name='gadevs.ga.',
        private_hosted_zone_name='private.lan.',
        zd_autoscaling_units=[
            {'unit_title': 'zdapp1',
             'elb_config': ElbConfig(
                 elb_listeners_config=elb_listeners_config,
                 elb_health_check='HTTP:80/index.html',
                 elb_log_bucket=None,
                 public_unit=True,
                 ssl_certificate_id=None,
                 healthy_threshold=10,
                 unhealthy_threshold=2,
                 interval=300,
                 timeout=30
             ),
             'blue_asg_config': AsgConfig(
                 minsize=1,
                 maxsize=1,
                 health_check_grace_period=300,
                 health_check_type='ELB',
                 image_id=app_image_id,
                 instance_type=instance_type,
                 iam_instance_profile_arn=None,
                 userdata=userdata1,
                 block_devices_config=block_devices_config,
                 simple_scaling_policy_config=None
             ),
             'green_asg_config': AsgConfig(
                 minsize=1,
                 maxsize=1,
                 health_check_grace_period=300,
                 health_check_type='ELB',
                 image_id=app_image_id,
                 instance_type=instance_type,
                 iam_instance_profile_arn=None,
                 userdata=userdata1,
                 block_devices_config=block_devices_config,
                 simple_scaling_policy_config=None
             ),
             'dependencies': ['app2', 'db1']}
        ],
        autoscaling_units=[{'unit_title': 'app1',
                            'asg_config': AsgConfig(
                                minsize=1,
                                maxsize=1,
                                health_check_grace_period=300,
                                health_check_type='ELB',
                                image_id=app_image_id,
                                instance_type=instance_type,
                                iam_instance_profile_arn=None,
                                userdata=userdata1,
                                block_devices_config=block_devices_config,
                                simple_scaling_policy_config=None
                            ),
                            'elb_config': ElbConfig(
                                elb_listeners_config=elb_listeners_config,
                                elb_health_check='HTTP:80/index.html',
                                elb_log_bucket=None,
                                public_unit=True,
                                ssl_certificate_id=None,
                                healthy_threshold=10,
                                unhealthy_threshold=2,
                                interval=300,
                                timeout=30
                            ),
                            'dependencies': ['app2', 'db1']},
                           {'unit_title': 'app2',
                            'asg_config': AsgConfig(
                                minsize=1,
                                maxsize=1,
                                health_check_grace_period=300,
                                health_check_type='ELB',
                                image_id=app_image_id,
                                instance_type=instance_type,
                                iam_instance_profile_arn=None,
                                userdata=userdata2,
                                block_devices_config=block_devices_config,
                                simple_scaling_policy_config=None
                            ),
                            'elb_config': ElbConfig(
                                elb_listeners_config=elb_listeners_config,
                                elb_health_check='HTTP:80/index.html',
                                elb_log_bucket=None,
                                public_unit=False,
                                ssl_certificate_id=None,
                                healthy_threshold=10,
                                unhealthy_threshold=2,
                                interval=300,
                                timeout=30
                            ),
                            'dependencies': []}
                           ],
        database_units=[{'unit_title': 'db1',
                         'database_config': DatabaseConfig(
                             db_instance_type='db.m1.small',
                             db_engine='postgres',
                             db_port='5432',
                             db_name='myDb',
                             db_hdd_size=5,
                             db_snapshot_id=None,
                             db_backup_window=None,
                             db_backup_retention=None,
                             db_maintenance_window=None,
                             db_storage_type=None
                         )
                         }],
        cf_distribution_units=[],
        api_gateway_units=[],
        lambda_units=[]
    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
