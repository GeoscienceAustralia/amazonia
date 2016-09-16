#!/usr/bin/python3

from amazonia.classes.elb import Elb
from amazonia.classes.elb_config import ElbConfig
from amazonia.classes.elb_listeners_config import ElbListenersConfig
from amazonia.classes.hosted_zone import HostedZone
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from amazonia.classes.sns import SNS
from troposphere import ec2, Ref, Tags, Template


def main():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    private_hosted_zone = HostedZone(template, 'myhostedzone.test.ga.', vpcs=[vpc])
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc),
                                                   DependsOn=internet_gateway.title))

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
    private_subnets = [template.add_resource(ec2.Subnet('MyPrivSub1',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.4.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub2',
                                                        AvailabilityZone='ap-southeast-2b',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.5.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub3',
                                                        AvailabilityZone='ap-southeast-2c',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.6.0/24'))]
    sns_topic = SNS(template)

    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        public_hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True,
        sns_topic=sns_topic
    )
    nat = SingleInstance(title='Nat',
                         template=template,
                         single_instance_config=single_instance_config)

    network_config = NetworkConfig(
        vpc=vpc,
        public_subnets=public_subnets,
        public_hosted_zone_name=None,
        private_hosted_zone=private_hosted_zone,
        private_subnets=private_subnets,
        jump=None,
        nat=nat,
        public_cidr=None,
        keypair=None,
        cd_service_role_arn=None,
        nat_highly_available=False,
        nat_gateways=[],
        sns_topic=sns_topic
    )

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP'
        ),
        ElbListenersConfig(
            instance_port='8080',
            loadbalancer_port='8080',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP'
        )
    ]

    elb_config1 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=False,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        sticky_app_cookies=['JSESSION', 'SESSIONTOKEN']
    )
    elb_config2 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        ssl_certificate_id='arn:aws:acm::tester',
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        sticky_app_cookies=['JSESSION', 'SESSIONTOKEN']
    )
    elb_config3 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        sticky_app_cookies=['JSESSION', 'SESSIONTOKEN']
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
    network_config.public_hosted_zone_name = 'myhostedzone.test.ga.'
    Elb(title='MyUnit3',
        network_config=network_config,
        elb_config=elb_config3,
        template=template
        )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
