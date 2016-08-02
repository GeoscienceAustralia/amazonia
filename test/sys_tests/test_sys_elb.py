#!/usr/bin/python3

from troposphere import ec2, Ref, Tags, Template, route53

from amazonia.classes.elb import Elb
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.elb_config import ElbConfig


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
    nat = SingleInstance(title='Nat',
                         keypair='pipeline',
                         si_image_id='ami-53371f30',
                         si_instance_type='t2.nano',
                         vpc=vpc,
                         subnet=public_subnets[0],
                         template=template,
                         instance_dependencies=vpc.title)

    network_config = NetworkConfig(
        vpc=vpc,
        public_subnets=public_subnets,
        unit_hosted_zone_name=hosted_zone.Name,
        private_subnets=None,
        jump=None,
        nat=nat,
        public_cidr=None
    )
    elb_config = ElbConfig(
        instanceports=['80'],
        loadbalancerports=['80'],
        protocols=['HTTP'],
        path2ping='/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True
    )

    Elb(title='MyUnit',
        network_config=network_config,
        elb_config=elb_config,
        template=template
        )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
