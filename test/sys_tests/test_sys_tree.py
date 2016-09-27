#!/usr/bin/python3

from amazonia.classes.tree import Tree


def main():
    nat_image_id = 'ami-53371f30'
    jump_image_id = 'ami-dc361ebf'
    instance_type = 't2.nano'

    stack = Tree(
        tree_name='tree',
        keypair='INSERT_YOUR_KEYPAIR_HERE',
        availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
        vpc_cidr={'name': 'VPC', 'cidr': '10.0.0.0/16'},
        jump_image_id=jump_image_id,
        jump_instance_type=instance_type,
        nat_highly_available=False,
        nat_image_id=nat_image_id,
        nat_instance_type=instance_type,
        iam_instance_profile_arn=None,
        owner_emails=[],
        home_cidrs=[{'name': 'GA', 'cidr': '123.123.12.34/32'}],
        public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
        public_hosted_zone_name='your.domain.',
        private_hosted_zone_name='private.lan.',
    )
    print(stack.template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
