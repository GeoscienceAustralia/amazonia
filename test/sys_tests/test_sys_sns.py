from amazonia.classes.sns import SNS
from troposphere import Template, ec2, Ref


def main():
    """
    Creates a troposphere template and then adds a single s3 bucket
    """
    template = Template()

    vpc = template.add_resource(ec2.VPC('MyVPC', CidrBlock='10.0.0.0/16'))
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway'))
    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                                        InternetGatewayId=Ref(internet_gateway),
                                                                        VpcId=Ref(vpc),
                                                                        DependsOn=internet_gateway.title))
    security_group = template.add_resource(ec2.SecurityGroup('mySecGroup',
                                                             GroupDescription='Security group',
                                                             VpcId=Ref(vpc),
                                                             ))

    subnet = template.add_resource(ec2.Subnet('MyPubSub',
                                              AvailabilityZone='ap-southeast-2a',
                                              VpcId=Ref(vpc),
                                              CidrBlock='10.0.1.0/24'))

    myinstance = template.add_resource(ec2.Instance(
        'myinstance',
        KeyName='INSERT_YOUR_KEYPAIR_HERE',
        ImageId='ami-dc361ebf',
        InstanceType='t2.nano',
        NetworkInterfaces=[ec2.NetworkInterfaceProperty(
            GroupSet=[Ref(security_group)],
            AssociatePublicIpAddress=True,
            DeviceIndex='0',
            DeleteOnTermination=True,
            SubnetId=Ref(subnets))],
        SourceDestCheck=True,
        DependsOn=internet_gateway.title
        ))

    mysns = SNS(unit_title='test',
                template=template,
                display_name='display_name')

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
