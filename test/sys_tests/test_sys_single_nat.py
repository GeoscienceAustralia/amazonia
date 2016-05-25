#!/usr/bin/env python

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
    SingleInstance(title='nat1',
                   keypair='pipeline',
                   si_image_id='ami-162c0c75',
                   si_instance_type='t2.micro',
                   vpc=vpc,
                   subnet=subnet,
                   template=template,
                   is_nat=True)

    template.add_resource(vpc)
    template.add_resource(subnet)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == "__main__":
    main()
