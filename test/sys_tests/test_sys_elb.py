#!/usr/bin/python3

from troposphere import ec2, Ref, Tags, Template, route53

from amazonia.classes.elb import Elb
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.single_instance_config import SingleInstanceConfig


def main():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    hosted_zone = template.add_resource(route53.HostedZone('MyHostedZone',
                                                           HostedZoneConfig=route53.HostedZoneConfiguration(
                                                               Comment='MyHostedZone'),
                                                           Name='myhostedzone.test.ga.',
                                                           VPCs=[route53.HostedZoneVPCs(VPCId=Ref(vpc),
                                                                                        VPCRegion='ap-southeast-2')]))

    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                                        InternetGatewayId=Ref(internet_gateway),
                                                                        VpcId=Ref(vpc)))
    gateway_attachment.DependsOn = internet_gateway.title

    public_subnets = [template.add_resource(ec2.Subnet('MyPubSub1',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.1.0/24')),
                      template.add_resource(ec2.Subnet('MyPubSub2',
                                                       AvailabilityZone='ap-southeast-2b',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24')),
                      template.add_resource(ec2.Subnet('MyPubSub3',
                                                       AvailabilityZone='ap-southeast-2c',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.3.0/24'))]
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        alert=None,
        alert_emails=None,
        hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )
    nat = SingleInstance(title='Nat',
                         template=template,
                         single_instance_config=single_instance_config)

    network_config = NetworkConfig(
        vpc=vpc,
        public_subnets=public_subnets,
        stack_hosted_zone_name=hosted_zone.Name,
        private_subnets=None,
        jump=None,
        nat=nat,
        public_cidr=None,
        keypair=None,
        cd_service_role_arn=None
    )
    elb_config1 = ElbConfig(
        instance_port=['80'],
        loadbalancer_port=['80'],
        loadbalancer_protocol=['HTTP'],
        instance_protocol=['HTTP'],
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        unit_hosted_zone_name=None,
        ssl_certificate_id=None
    )
    elb_config2 = ElbConfig(
        instance_port=['80'],
        loadbalancer_port=['443'],
        loadbalancer_protocol=['HTTPS'],
        instance_protocol=['HTTP'],
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        unit_hosted_zone_name=None,
        ssl_certificate_id='arn:aws:acm::tester'
    )

    Elb(title='MyUnit1',
        network_config=network_config,
        elb_config=elb_config1,
        template=template
        )

    Elb(title='MyUnit2',
        network_config=network_config,
        elb_config=elb_config2,
        template=template
        )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
