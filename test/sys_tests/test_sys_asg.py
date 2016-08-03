#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from troposphere import ec2, Ref, Template

from amazonia.classes.asg import Asg
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.network_config import NetworkConfig


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
        stack_hosted_zone_name=None
    )

    asg_config = AsgConfig(
        keypair='pipeline',
        image_id='ami-dc361ebf',
        instance_type='t2.nano',
        minsize=1,
        maxsize=1,
        userdata=userdata,
        health_check_grace_period=300,
        health_check_type='ELB',
        cd_service_role_arn='arn:aws:iam::12345678987654321:role/CodeDeployServiceRole',
        iam_instance_profile_arn='arn:aws:iam::12345678987654321:role/InstanceProfileRole',
        sns_topic_arn='arn:aws:sns:ap-southeast-2:123456789:test_sns_arn',
        sns_notification_types=['autoscaling:EC2_INSTANCE_LAUNCH',
                                'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                                'autoscaling:EC2_INSTANCE_TERMINATE',
                                'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'],
        hdd_size=None
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
