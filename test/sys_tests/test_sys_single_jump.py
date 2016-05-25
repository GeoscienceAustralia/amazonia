from amazonia.classes.single_instance import SingleInstance
from troposphere import ec2, Ref, Template


def main():
    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')
    template = Template()
    SingleInstance(title='jump',
                   keypair='pipeline',
                   si_image_id='ami-05446966',
                   si_instance_type='t2.micro',
                   vpc=vpc,
                   subnet=subnet,
                   template=template)

    template.add_resource(vpc)
    template.add_resource(subnet)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == "__main__":
    main()
