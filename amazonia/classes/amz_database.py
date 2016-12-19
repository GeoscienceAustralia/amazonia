#!/usr/bin/python3

from amazonia.classes.leaf import Leaf
from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject
from troposphere import ImportValue, Export
from troposphere import Tags, Ref, rds, Join, Output, GetAtt, Parameter, route53


class Database(LocalSecurityEnabledObject):
    def __init__(self, title, template, network_config, database_config):
        """
         Class to create an RDS and DB subnet group in a vpc
         http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
         https://github.com/cloudtools/troposphere/blob/master/troposphere/rds.py
         :param title: Title of the RDS and associated resources to be used in cloud formation
         :param template: Troposphere stack to append resources to
         :param network_config: object containing network related variables
         :param database_config: object containing database related variables
         """
        super(Database, self).__init__(template=template, title=title, vpc=network_config.vpc)
        self.network_config = network_config
        self.db_subnet_group_title = title + 'Dsg'
        self.port = database_config.db_port
        self.rds_r53 = None
        # Add Tags
        tags = Tags(Name=self.db_subnet_group_title)
        tags += Tags(owner=database_config.owner)
        self.trop_db_subnet_group = template.add_resource(
            rds.DBSubnetGroup(self.db_subnet_group_title,
                              DBSubnetGroupDescription=self.db_subnet_group_title,
                              SubnetIds=network_config.private_subnets,
                              Tags=tags))
        rds_params = {
            'AllocatedStorage': database_config.db_hdd_size,
            'AllowMajorVersionUpgrade': True,
            'AutoMinorVersionUpgrade': True,
            'MultiAZ': True,
            'DBInstanceClass': database_config.db_instance_type,
            'DBSubnetGroupName': Ref(self.trop_db_subnet_group),
            'DBName': database_config.db_name,
            'DBInstanceIdentifier': Join('', [Ref('AWS::StackName'), self.title]),
            'Engine': database_config.db_engine,
            'Port': self.port,
            'VPCSecurityGroups': [self.security_group],
            'Tags': Tags(Name=Join('', [Ref('AWS::StackName'), '-', self.title]))
        }

        # Optional RDS Params
        opt_rds_params = {
            'PreferredBackupWindow': database_config.db_backup_window,
            'BackupRetentionPeriod': database_config.db_backup_retention,
            'PreferredMaintenanceWindow': database_config.db_maintenance_window,
            'StorageType': database_config.db_storage_type,
        }

        for k, v in opt_rds_params.items():
            if v is not None:
                rds_params[k] = v

        # Remove username and password if SnapshotID present
        if database_config.db_snapshot_id is None:
            self.username = self.template.add_parameter(Parameter(
                self.title + 'MasterUsername', Type='String',
                Description='Master username of {0} RDS'.format(self.title),
                NoEcho=True))

            self.password = self.template.add_parameter(Parameter(
                self.title + 'MasterPassword', Type='String',
                Description='Master password of {0} RDS'.format(self.title),
                NoEcho=True))
            rds_params['MasterUsername'] = Ref(self.username)
            rds_params['MasterUserPassword'] = Ref(self.password)
        else:
            rds_params['DBSnapshotIdentifier'] = database_config.db_snapshot_id
            rds_params['DBName'] = ''

        # Create RDS
        self.trop_db = template.add_resource(rds.DBInstance(self.title,
                                                            **rds_params))

        self.create_r53_record()

    def create_r53_record(self):
        """
        Function to create r53 recourdset to associate with the RDS
        """
        self.rds_r53 = self.template.add_resource(route53.RecordSetGroup(
            self.title + 'R53',
            HostedZoneId=self.network_config.private_hosted_zone_id,
            RecordSets=[route53.RecordSet(
                Name=Join('', [self.title,
                               '.',
                               self.network_config.private_hosted_zone_domain]),
                ResourceRecords=[GetAtt(self.trop_db, 'Endpoint.Address')],
                TTL=300,
                Type='CNAME')]))

        self.template.add_output(Output(
            self.trop_db.title + 'Endpoint',
            Description='Address of the {0} RDS'.format(self.title),
            Value=Join('', [self.rds_r53.RecordSets[0].Name, ':', GetAtt(self.trop_db, 'Endpoint.Port')])))


class DatabaseLeaf(Database, Leaf):
    def __init__(self, leaf_title, availability_zones, template, tree_name, database_config):
        """
        Create an RDS as a leaf, part of cross referenced stack
        :param leaf_title: title of the API Gateway as part of cross referenced stack
        :param availability_zones: List of availability zones RDS resources can use
        :param tree_name: name of cross referenced stack
        :param template: Troposphere stack to append resources to
        :param database_config: object containing database related variables
        """
        self.leaf_title = leaf_title
        self.availability_zones = availability_zones
        self.tree_name = tree_name
        self.tree_config = None
        self.set_tree_config(template=template, availability_zones=availability_zones,
                             tree_name=tree_name)
        self.tree_config.private_hosted_zone_id = ImportValue(self.tree_name + '-PrivateHostedZoneId')
        self.tree_config.private_hosted_zone_domain = ImportValue(self.tree_name + '-PrivateHostedZoneDomain')
        super(DatabaseLeaf, self).__init__(template=template, title=leaf_title, network_config=self.tree_config,
                                           database_config=database_config)

        self.template.add_output(Output(
            'rdsSecurityGroup',
            Description='RDS Security group',
            Value=self.security_group,
            Export=Export(self.tree_name + '-' + self.leaf_title + '-SecurityGroup')
        ))


class DatabaseUnit(Database):
    def __init__(self, unit_title, template, stack_config, database_config):
        """
        Create an RDS as a unit, part of an integrated stack
        :param unit_title: title of the RDS as part of an integrated stack
        :param title: Title of the RDS and associated resources to be used in cloud formation
        :param template: Troposphere stack to append resources to
        :param network_config: object containing network related variables
        :param database_config: object containing database related variables
        """
        self.stack_config = stack_config
        super(DatabaseUnit, self).__init__(title=unit_title, template=template, network_config=stack_config,
                                           database_config=database_config)
