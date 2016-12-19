from amazonia.classes.network import Network
from amazonia.classes.stack_config import NetworkConfig
from troposphere import Ref


def get_network_config():
    network = Network('INSERT_YOUR_KEYPAIR_HERE',
                      ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
                      vpc_cidr={'name': 'VPC', 'cidr': '10.0.0.0/16'},
                      home_cidrs=[{'name': 'Home', 'cidr': '0.0.0.0/0'}],
                      public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
                      jump_image_id='ami-dc361ebf',
                      jump_instance_type='t2.nano',
                      nat_image_id='ami-53371f30',
                      nat_instance_type='t2.nano',
                      public_hosted_zone_name='your.domain.',
                      private_hosted_zone_name='private.lan.',
                      iam_instance_profile_arn='arn:aws:iam::123456789:instance-profile/am-instance-profile',
                      owner_emails=[],
                      nat_highly_available=False,
                      ec2_scheduled_shutdown=False,
                      owner='autobots')

    service_role_arn = 'arn:aws:iam::123456789:role/CodeDeployServiceRole'

    return NetworkConfig(
        vpc=network.vpc,
        jump=network.jump,
        nat=network.nat,
        public_subnets=[Ref(subnet) for subnet in network.public_subnets],
        private_subnets=[Ref(subnet) for subnet in network.private_subnets],
        public_cidr=network.public_cidr,
        public_hosted_zone_name=network.public_hosted_zone_name,
        private_hosted_zone_id=Ref(network.private_hosted_zone.trop_hosted_zone),
        private_hosted_zone_domain=network.private_hosted_zone.domain,
        keypair=network.keypair,
        cd_service_role_arn=service_role_arn,
        nat_highly_available=network.nat_highly_available,
        nat_gateways=[],
        sns_topic=Ref(network.sns_topic.trop_topic),
        availability_zones=network.availability_zones
    ), network.template
