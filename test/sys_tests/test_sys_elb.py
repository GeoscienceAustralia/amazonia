#!/usr/bin/python3

from troposphere import ec2, Ref, Tags, Template, route53

from amazonia.classes.elb import Elb


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

    Elb(title='MyUnit',
        instanceports=['80'],
        loadbalancerports=['80'],
        subnets=public_subnets,
        protocols=['HTTP'],
        vpc=vpc,
        hosted_zone_name=hosted_zone.Name,
        path2ping='/index.html',
        template=template,
        gateway_attachment=gateway_attachment,
        elb_log_bucket='my-s3-bucket')

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == "__main__":
    main()
