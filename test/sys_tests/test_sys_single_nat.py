#!/usr/bin/env python

from troposphere import ec2, Ref, Template

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig


def main():
    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')
    template = Template()
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.micro',
        vpc=vpc,
        subnet=subnet,
        is_nat=True,
        instance_dependencies=vpc.title,
        hosted_zone_name=None,
        alert=False,
        alert_emails=[],
        iam_instance_profile_arn=None
    )
    SingleInstance(title='nat1',
                   template=template,
                   single_instance_config=single_instance_config
                   )

    template.add_resource(vpc)
    template.add_resource(subnet)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
