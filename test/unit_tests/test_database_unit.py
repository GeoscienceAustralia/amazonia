from nose.tools import *
from troposphere import ec2, Ref, Tags, Template
from amazonia.classes.database_unit import DatabaseUnit, InvalidFlowError

"""
Tests the functions of the Database Unit class
"""

def test_database():
    """
    Tests correct structure of Database unit.
    """
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
    db = DatabaseUnit(unit_title='MyDb',
                      subnets=private_subnets,
                      vpc=vpc,
                      template=template,
                      db_instance_type='db.t2.micro',
                      db_engine='postgres',
                      db_port='5432',
                      db_name='MyDb',
                      db_snapshot_id=None,
                      db_hdd_size=5)

    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, 'MyDb')
    assert_equals(len(template.outputs), 1)
    assert_equals(len(template.parameters), 2)
    assert_equals(db.trop_db.AllocatedStorage, 5)

    assert_raises(InvalidFlowError, db.add_unit_flow, **{'receiver': db})


def test_databse_snapshot():
    """
    Tests correct structure of Database provisioned from snapshot.
    """
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
    db = DatabaseUnit(unit_title='MyDb',
                      subnets=private_subnets,
                      vpc=vpc,
                      template=template,
                      db_instance_type='db.t2.micro',
                      db_hdd_size=5,
                      db_engine='postgres',
                      db_snapshot_id='ss123456789v00-final-snapshot',
                      db_port='5432',
                      db_name='MyDb')

    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, '')
    assert_equals(len(template.outputs), 1)
    assert_equals(len(template.parameters), 0)
    assert_equals(db.trop_db.AllocatedStorage, 5)
