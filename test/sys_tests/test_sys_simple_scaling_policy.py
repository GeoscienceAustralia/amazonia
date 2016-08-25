#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.asg import Asg
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.simple_scaling_policy_config import SimpleScalingPolicyConfig
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

    network_config = NetworkConfig(
        vpc=vpc,
        private_subnets=subnets,
        public_subnets=None,
        jump=None,
        nat=None,
        public_cidr=None,
        stack_hosted_zone_name=None,
        keypair='pipeline',
        cd_service_role_arn='arn:aws:iam::12345678987654321:role/CodeDeployServiceRole'
    )

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
        block_devices_config=None,
        simple_scaling_policy_config=simple_scaling_policy_config
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
