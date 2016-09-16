#!/usr/bin/python3

from amazonia.classes.sns import SNS
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.database_unit import DatabaseUnit
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.hosted_zone import HostedZone
from troposphere import ec2, Ref, Tags, Template


def main():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc),
                                                   DependsOn=internet_gateway.title))

    private_subnets = [template.add_resource(ec2.Subnet('MyPubSub1',
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
    private_hosted_zone = HostedZone(vpcs=[vpc], template=template, domain='private.lan.')
    sns_topic = SNS(template)
    network_config = NetworkConfig(
        public_subnets=None,
        vpc=vpc,
        private_subnets=private_subnets,
        jump=None,
        nat=None,
        public_cidr=None,
        public_hosted_zone_name=None,
        private_hosted_zone=private_hosted_zone,
        keypair=None,
        cd_service_role_arn=None,
        nat_highly_available=False,
        nat_gateways=[],
        sns_topic=sns_topic
    )

    database_config = DatabaseConfig(
        db_instance_type='db.t2.micro',
        db_engine='postgres',
        db_port='5432',
        db_name='myDb',
        db_hdd_size='5',
        db_snapshot_id=None,
        db_backup_window='17:00-17:30',
        db_backup_retention='4',
        db_maintenance_window='Mon:01:00-Mon:01:30',
        db_storage_type='gp2'
    )

    # Test RDS
    DatabaseUnit(unit_title='MyDb',
                 network_config=network_config,
                 template=template,
                 database_config=database_config
                 )

    # Test RDS with SnapshotID
    database_config.db_snapshot_id = 'amazonia-verbose-snapshot'

    DatabaseUnit(unit_title='MyDb2',
                 network_config=network_config,
                 template=template,
                 database_config=database_config
                 )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
