#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.asg import Asg
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.block_devices_config import BlockDevicesConfig
from amazonia.classes.network_config import NetworkConfig
from troposphere import ec2, Ref, Template


def main():
    template = Template()

    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    subnets = [template.add_resource(ec2.Subnet('MySubnet',
                                                AvailabilityZone='ap-southeast-2a',
                                                VpcId=Ref(vpc),
                                                CidrBlock='10.0.1.0/24'))]

    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway'))
    template.add_resource(ec2.VPCGatewayAttachment('MyInternetGatewayAttachment',
                                                   VpcId=Ref(vpc),
                                                   InternetGatewayId=Ref(internet_gateway)
                                                   ))

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
                                                           Subnets=[Ref(subnet) for subnet in subnets]))

    class Single(object):
        def __init__(self):
            self.single = ec2.Instance('title')

    network_config = NetworkConfig(
        vpc=vpc,
        private_subnets=subnets,
        public_subnets=None,
        jump=None,
        nat=Single(),
        public_cidr=None,
        public_hosted_zone_name=None,
        private_hosted_zone=None,
        keypair='pipeline',
        cd_service_role_arn='arn:aws:iam::12345678987654321:role/CodeDeployServiceRole',
        nat_highly_available=False,
        nat_gateways=[]
    )

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
        maxsize=1,
        userdata='',
        health_check_grace_period=300,
        health_check_type='ELB',
        iam_instance_profile_arn='arn:aws:iam::12345678987654321:role/InstanceProfileRole',
        sns_topic_arn='arn:aws:sns:ap-southeast-2:123456789:test_sns_arn',
        sns_notification_types=['autoscaling:EC2_INSTANCE_LAUNCH',
                                'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                                'autoscaling:EC2_INSTANCE_TERMINATE',
                                'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'],
        block_devices_config=block_devices_config,
        simple_scaling_policy_config=None
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
