from amazonia.classes.amz_database import DatabaseUnit, DatabaseLeaf
from amazonia.classes.database_config import DatabaseConfig
from network_setup import get_network_config
from nose.tools import *
from troposphere import Join

template = network_config = database_config = tree_name = availability_zones = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, database_config, tree_name, availability_zones

    network_config, template = get_network_config()
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    tree_name = 'testtree'

    database_config = DatabaseConfig(
        db_instance_type='db.t2.micro',
        db_engine='postgres',
        db_port='5432',
        db_name='MyDb',
        db_snapshot_id=None,
        db_hdd_size=5,
        db_backup_window='17:00-17:30',
        db_backup_retention='4',
        db_maintenance_window='Mon:01:00-Mon:01:30',
        db_storage_type='gp2'
    )


@with_setup(setup_resources)
def test_database_leaf():
    """ Tests correct structure of Database leaf.
    """
    global network_config, database_config, template
    db = DatabaseLeaf(leaf_title='MyDb',
                      tree_name=tree_name,
                      template=template,
                      database_config=database_config,
                      availability_zones=availability_zones
                      )

    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, 'MyDb')
    assert_equals(len(template.outputs), 3)
    assert_equals(len(template.parameters), 2)
    assert_equals(db.trop_db.AllocatedStorage, 5)
    assert_equals(db.trop_db.PreferredBackupWindow, '17:00-17:30'),
    assert_equals(db.trop_db.BackupRetentionPeriod, '4'),
    assert_equals(db.trop_db.PreferredMaintenanceWindow, 'Mon:01:00-Mon:01:30'),
    assert_equals(db.trop_db.StorageType, 'gp2')
    assert_equals(type(db.trop_db.DBInstanceIdentifier), Join)



@with_setup(setup_resources)
def test_database_unit():
    """ Tests correct structure of Database unit.
    """
    global network_config, database_config, template
    db = DatabaseUnit(unit_title='MyDb',
                      stack_config=network_config,
                      template=template,
                      database_config=database_config
                      )

    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, 'MyDb')
    assert_equals(len(template.outputs), 2)
    assert_equals(len(template.parameters), 2)
    assert_equals(db.trop_db.AllocatedStorage, 5)
    assert_equals(db.trop_db.PreferredBackupWindow, '17:00-17:30'),
    assert_equals(db.trop_db.BackupRetentionPeriod, '4'),
    assert_equals(db.trop_db.PreferredMaintenanceWindow, 'Mon:01:00-Mon:01:30'),
    assert_equals(db.trop_db.StorageType, 'gp2')
    assert_equals(type(db.trop_db.DBInstanceIdentifier), Join)


@with_setup(setup_resources)
def test_databse_snapshot():
    """ Tests correct structure of Database provisioned from snapshot.
        """
    global network_config, database_config, template
    database_config.db_snapshot_id = 'ss123456789v00-final-snapshot'

    db = DatabaseUnit(unit_title='MyDb',
                      stack_config=network_config,
                      template=template,
                      database_config=database_config
                      )

    assert_equals(db.trop_db.DBInstanceClass, 'db.t2.micro')
    assert_equals(db.trop_db.Engine, 'postgres')
    assert_equals(db.trop_db.Port, '5432')
    assert_equals(db.trop_db.DBName, '')
    assert_equals(len(template.outputs), 2)
    assert_equals(len(template.parameters), 0)
    assert_equals(db.trop_db.AllocatedStorage, 5)
    assert_equals(type(db.trop_db.DBInstanceIdentifier), Join)
