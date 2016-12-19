#!/usr/bin/python3

from amazonia.classes.database_config import DatabaseConfig
from amazonia.classes.amz_database import DatabaseLeaf
from troposphere import Template


def main():
    template = Template()

    database_config = DatabaseConfig(
        db_instance_type='db.t2.micro',
        db_engine='postgres',
        db_port='5432',
        db_name='myDb',
        db_hdd_size='5',
        db_snapshot_id=None,
        db_backup_window=None,
        db_backup_retention=None,
        db_maintenance_window=None,
        db_storage_type='gp2',
        owner='autobots'
    )

    DatabaseLeaf(leaf_title='MyDb',
                 tree_name='tree',
                 template=template,
                 database_config=database_config,
                 availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
                 )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
