#!/usr/bin/python3

from amazonia.classes.amz_database import DatabaseUnit
from amazonia.classes.database_config import DatabaseConfig
from network_setup import get_network_config


def main():
    network_config, template = get_network_config()
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
        db_storage_type='gp2',
        owner='ga.autobots@gmail.com'
    )

    # Test RDS
    DatabaseUnit(unit_title='MyDb',
                 stack_config=network_config,
                 template=template,
                 database_config=database_config
                 )

    # Test RDS with SnapshotID
    database_config.db_snapshot_id = 'amazonia-verbose-snapshot'

    DatabaseUnit(unit_title='MyDb2',
                 stack_config=network_config,
                 template=template,
                 database_config=database_config
                 )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
