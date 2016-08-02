from nose.tools import *
from troposphere import ec2, Ref, Tags, Template
from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.database_unit import DatabaseUnit, InvalidFlowError

template = network_config = database_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, database_config

    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    gateway_attachment = template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                                        InternetGatewayId=Ref(internet_gateway),
                                                                        VpcId=Ref(vpc)))
    gateway_attachment.DependsOn = internet_gateway.title

    private_subnets = [template.add_resource(ec2.Subnet('MyPrivSub1',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub2',
                                                        AvailabilityZone='ap-southeast-2b',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.2.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub3',
                                                        AvailabilityZone='ap-southeast-2c',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.3.0/24'))]
    network_config = NetworkConfig(
        public_cidr=None,
        vpc=vpc,
        public_subnets=None,
        private_subnets=private_subnets,
        jump=None,
        nat=None,
        unit_hosted_zone_name=None
    )

    database_config = DatabaseConfig(
        db_instance_type='db.t2.micro',
        db_engine='postgres',
        db_port='5432',
        db_name='MyDb',
        db_snapshot_id=None,
        db_hdd_size=5
    )


@with_setup(setup_resources)
def test_database():
    """ Tests correct structure of Database unit.
    """
    global network_config, database_config, template
    db = DatabaseUnit(unit_title='MyDb',
                      network_config=network_config,
                      template=template,
                      database_config=database_config
                      )


    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, 'MyDb')
    assert_equals(len(template.outputs), 1)
    assert_equals(len(template.parameters), 2)
    assert_equals(db.trop_db.AllocatedStorage, 5)

    assert_raises(InvalidFlowError, db.add_unit_flow, **{'receiver': db})


@with_setup(setup_resources)
def test_databse_snapshot():
    """ Tests correct structure of Database provisioned from snapshot.
        """
    global network_config, database_config, template
    database_config.db_snapshot_id = 'ss123456789v00-final-snapshot'

    db = DatabaseUnit(unit_title='MyDb',
                      network_config=network_config,
                      template=template,
                      database_config=database_config
                      )


    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, '')
    assert_equals(len(template.outputs), 1)
    assert_equals(len(template.parameters), 0)
    assert_equals(db.trop_db.AllocatedStorage, 5)
