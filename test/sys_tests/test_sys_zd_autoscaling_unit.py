#!/usr/bin/python3

from troposphere import ec2, Ref, Template, Join, Tags

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.zd_autoscaling_unit import ZdAutoscalingUnit
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.asg_config import AsgConfig
from amazonia.classes.elb_config import ElbConfig
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
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=internet_gateway.title,
        is_nat=True,
        alert=None,
        alert_emails=None,
        hosted_zone_name=None,
        iam_instance_profile_arn=None
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

    cd_service_role_arn = 'arn:aws:iam::1234567890124 :role/CodeDeployServiceRole'

    network_config = NetworkConfig(public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
                                   vpc=vpc,
                                   public_subnets=public_subnets,
                                   private_subnets=private_subnets,
                                   nat=nat,
                                   jump=jump,
                                   stack_hosted_zone_name=None,
                                   cd_service_role_arn=cd_service_role_arn,
                                   keypair='pipeline')
    loadbalancer_protocol = ['HTTP']
    instance_protocol = ['HTTP']
    instance_port = ['80']
    loadbalancer_port = ['80']
    elb_health_check = 'HTTP:80/index.html'
    minsize = 1
    maxsize = 1
    health_check_grace_period = 300
    health_check_type = 'ELB'

    image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'

    block_devices_config = [{
            'device_name': '/dev/xvda',
            'ebs_volume_size': '15',
            'ebs_volume_type': 'gp2',
            'ebs_encrypted': False,
            'ebs_snapshot_id': '',
            'virtual_name': False}]

    elb_config = ElbConfig(loadbalancer_protocol=loadbalancer_protocol,
                           instance_protocol=instance_protocol,
                           instance_port=instance_port,
                           loadbalancer_port=loadbalancer_port,
                           elb_log_bucket=None,
                           elb_health_check=elb_health_check,
                           public_unit=True,
                           unit_hosted_zone_name=None,
                           ssl_certificate_id=None)
    blue_asg_config = AsgConfig(sns_topic_arn=None,
                                sns_notification_types=None,
                                health_check_grace_period=health_check_grace_period,
                                health_check_type=health_check_type,
                                minsize=minsize,
                                maxsize=maxsize,
                                image_id=image_id,
                                instance_type=instance_type,
                                userdata=userdata,
                                iam_instance_profile_arn=None,
                                block_devices_config=block_devices_config)
    green_asg_config = AsgConfig(sns_topic_arn=None,
                                 sns_notification_types=None,
                                 health_check_grace_period=health_check_grace_period,
                                 health_check_type=health_check_type,
                                 minsize=minsize,
                                 maxsize=maxsize,
                                 image_id=image_id,
                                 instance_type=instance_type,
                                 userdata=userdata,
                                 iam_instance_profile_arn=None,
                                 block_devices_config=block_devices_config)

    unit1 = ZdAutoscalingUnit(
        unit_title='app1',
        template=template,
        dependencies=['app2'],
        network_config=network_config,
        elb_config=elb_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    unit2 = ZdAutoscalingUnit(
        unit_title='app2',
        template=template,
        dependencies=['app1'],
        network_config=network_config,
        elb_config=elb_config,
        blue_asg_config=blue_asg_config,
        green_asg_config=green_asg_config
    )

    unit1.add_unit_flow(unit2)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
