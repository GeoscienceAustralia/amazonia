#!/usr/bin/env python

from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from troposphere import ec2, Ref, Template


def main():
    vpc = ec2.VPC('MyVPC',
                  CidrBlock='10.0.0.0/16')
    subnet = ec2.Subnet('MySubnet',
                        AvailabilityZone='ap-southeast-2a',
                        VpcId=Ref(vpc),
                        CidrBlock='10.0.1.0/24')
    template = Template()
    single_instance_config = SingleInstanceConfig(
        keypair='INSERT_YOUR_KEYPAIR_HERE',
        si_image_id='ami-dc361ebf',
        si_instance_type='t2.micro',
        vpc=Ref(vpc),
        subnet=Ref(subnet),
        instance_dependencies=vpc.title,
        public_hosted_zone_name=None,
        sns_topic=None,
        is_nat=False,
        iam_instance_profile_arn=None,
        availability_zone='ap-southeast-2a',
        ec2_scheduled_shutdown=None
    )
    SingleInstance(title='jump',
                   template=template,
                   single_instance_config=single_instance_config
                   )

    template.add_resource(vpc)
    template.add_resource(subnet)
    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
