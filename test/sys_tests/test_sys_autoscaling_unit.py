#!/usr/bin/python3

from troposphere import ec2, Ref, Template, Join, Tags

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.autoscaling_unit import AutoscalingUnit


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
        ec2.InternetGateway('igname', Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', 'igname']))))
    internet_gateway.DependsOn = vpc.title

    gateway_attachment = template.add_resource(
        ec2.VPCGatewayAttachment(internet_gateway.title + 'Atch',
                                 VpcId=Ref(vpc),
                                 InternetGatewayId=Ref(internet_gateway)))
    gateway_attachment.DependsOn = internet_gateway.title

    private_subnets = [template.add_resource(ec2.Subnet('MySubnet',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24'))]
    public_subnets = [template.add_resource(ec2.Subnet('MySubnet2',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24'))]
    nat = SingleInstance(title='nat',
                         keypair='pipeline',
                         si_image_id='ami-162c0c75',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         template=template)
    nat.DependsOn = internet_gateway.title

    jump = SingleInstance(title='jump',
                          keypair='pipeline',
                          si_image_id='ami-162c0c75',
                          si_instance_type='t2.nano',
                          vpc=vpc,
                          subnet=public_subnets[0],
                          template=template)

    jump.DependsOn = internet_gateway.title

    service_role_arn = 'arn:aws:iam::658691668407:role/CodeDeployServiceRole'

    unit1 = AutoscalingUnit(
        unit_title='app1',
        vpc=vpc,
        template=template,
        protocols=['HTTP'],
        instanceports=['80'],
        loadbalancerports=['80'],
        path2ping='/index.html',
        public_subnets=public_subnets,
        private_subnets=private_subnets,
        minsize=1,
        maxsize=1,
        health_check_grace_period=300,
        health_check_type='ELB',
        keypair='pipeline',
        image_id='ami-05446966',
        instance_type='t2.nano',
        userdata=userdata,
        cd_service_role_arn=service_role_arn,
        nat=nat,
        jump=jump,
        hosted_zone_name=None,
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        elb_log_bucket=None,
        gateway_attachment=gateway_attachment,
        dependencies='app2'
    )

    unit2 = AutoscalingUnit(
        unit_title='app2',
        vpc=vpc,
        template=template,
        protocols=['HTTP'],
        instanceports=['80'],
        loadbalancerports=['80'],
        path2ping='/index.html',
        public_subnets=public_subnets,
        private_subnets=private_subnets,
        minsize=1,
        maxsize=1,
        health_check_grace_period=300,
        health_check_type='ELB',
        keypair='pipeline',
        image_id='ami-05446966',
        instance_type='t2.nano',
        userdata=userdata,
        cd_service_role_arn=service_role_arn,
        nat=nat,
        jump=jump,
        hosted_zone_name=None,
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        iam_instance_profile_arn=None,
        sns_topic_arn=None,
        sns_notification_types=None,
        elb_log_bucket=None,
        gateway_attachment=gateway_attachment,
        dependencies='app1'
    )

    unit1.add_unit_flow(unit2)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
