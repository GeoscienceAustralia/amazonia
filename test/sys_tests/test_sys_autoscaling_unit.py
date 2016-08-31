#!/usr/bin/python3

from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.autoscaling_unit import AutoscalingUnit
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from troposphere import ec2, Ref, Template, Join, Tags


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

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    internet_gateway = template.add_resource(
        ec2.InternetGateway('igname',
                            Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', 'igname'])),
                            DependsOn=vpc.title))

    gateway_attachment = template.add_resource(
        ec2.VPCGatewayAttachment(internet_gateway.title + 'Atch',
                                 VpcId=Ref(vpc),
                                 InternetGatewayId=Ref(internet_gateway),
                                 DependsOn=internet_gateway.title))

    private_subnets = [template.add_resource(ec2.Subnet('MySubnet',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24'))]
    public_subnets = [template.add_resource(ec2.Subnet('MySubnet2',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24'))]
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=internet_gateway.title,
        alert=None,
        alert_emails=None,
        hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )
    nat = SingleInstance(title='nat',
                         template=template,
                         single_instance_config=single_instance_config
                         )

    single_instance_config.si_image_id = 'ami-dc361ebf'
    single_instance_config.is_nat = False

    jump = SingleInstance(title='jump',
                          template=template,
                          single_instance_config=single_instance_config)

    service_role_arn = 'arn:aws:iam::1234567890124 :role/CodeDeployServiceRole'

    network_config = NetworkConfig(
        vpc=vpc,
        jump=jump,
        nat=nat,
        private_subnets=private_subnets,
        public_subnets=public_subnets,
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        stack_hosted_zone_name=None,
        keypair='pipeline',
        cd_service_role_arn=service_role_arn
    )
    elb_config = ElbConfig(
        instance_protocol=['HTTP'],
        loadbalancer_protocol=['HTTP'],
        instance_port=['80'],
        loadbalancer_port=['80'],
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket=None,
        public_unit=True,
        unit_hosted_zone_name=None,
        ssl_certificate_id=None
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
        maxsize=1,
        health_check_grace_period=300,
        health_check_type='ELB',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        userdata=userdata,
        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None
    )

    unit1 = AutoscalingUnit(
        unit_title='app1',
        template=template,
        dependencies='app2',
        network_config=network_config,
        elb_config=elb_config,
        asg_config=asg_config
    )

    unit2 = AutoscalingUnit(
        unit_title='app2',
        network_config=network_config,
        template=template,
        elb_config=elb_config,
        asg_config=asg_config,
        dependencies='app1'
    )

    unit1.add_unit_flow(unit2)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
