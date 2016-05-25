#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from troposphere import ec2, Ref, Template

from amazonia.classes.asg import Asg


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

    Asg(title='simple',
        keypair='pipeline',
        image_id='ami-05446966',
        instance_type='t2.nano',
        vpc=vpc,
        subnets=subnets,
        minsize=1,
        maxsize=1,
        load_balancer=load_balancer,
        userdata=userdata,
        health_check_grace_period=300,
        health_check_type='ELB',
        cd_service_role_arn='arn:aws:iam::658691668407:role/CodeDeployServiceRole',
        iam_instance_profile_arn=
        'arn:aws:iam::658691668407:instance-profile/natmap-iam-instance-profile-InstanceProfile-1XCAISNTXMEHG',
        sns_topic_arn='arn:aws:sns:ap-southeast-2:074615718262:natmap_service_status',
        sns_notification_types=['autoscaling:EC2_INSTANCE_LAUNCH',
                                'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                                'autoscaling:EC2_INSTANCE_TERMINATE',
                                'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'],
        template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
