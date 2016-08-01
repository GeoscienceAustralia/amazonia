#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, rds, Join, Output, GetAtt, Parameter


class DatabaseUnit(SecurityEnabledObject):
    def __init__(self, unit_title, template, network_config, database_config):
        """
        Class to create an RDS and DB subnet group in a vpc
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/rds.py
        :param unit_title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param template: Troposphere stack to append resources to
        :param network_config: object containing network related variables
        :param database_config: object containing database related variablea
        """
        self.title = unit_title + 'Rds'
        self.dependencies = []
        self.db_subnet_group_title = unit_title + 'Dsg'
        self.port = database_config.db_port
        super(DatabaseUnit, self).__init__(vpc=network_config.vpc, title=self.title, template=template)

        self.trop_db_subnet_group = template.add_resource(
            rds.DBSubnetGroup(self.db_subnet_group_title,
                              DBSubnetGroupDescription=self.db_subnet_group_title,
                              SubnetIds=[Ref(x) for x in network_config.private_subnets],
                              Tags=Tags(Name=self.db_subnet_group_title)))
        rds_params = {
            'AllocatedStorage': database_config.db_hdd_size,
            'AllowMajorVersionUpgrade': True,
            'AutoMinorVersionUpgrade': True,
            'MultiAZ': True,
            'DBInstanceClass': database_config.db_instance_type,
            'DBSubnetGroupName': Ref(self.trop_db_subnet_group),
            'DBName': database_config.db_name,
            'Engine': database_config.db_engine,
            'Port': self.port,
            'VPCSecurityGroups': [Ref(self.security_group)],
            'Tags': Tags(Name=Join('', [Ref('AWS::StackName'), '-', self.title]))
        }
        if database_config.db_snapshot_id is None:
            self.username = self.template.add_parameter(Parameter(
                self.title + 'Username', Type='String', Description='Master username of {0} RDS'.format(self.title),
                NoEcho=True))

            self.password = self.template.add_parameter(Parameter(
                self.title + 'Password', Type='String', Description='Master password of {0} RDS'.format(self.title),
                NoEcho=True))
            rds_params['MasterUsername'] = Ref(self.username)
            rds_params['MasterUserPassword'] = Ref(self.password)
        else:
            rds_params['DBSnapshotIdentifier'] = database_config.db_snapshot_id

        self.trop_db = template.add_resource(rds.DBInstance(self.title, **rds_params))

        self.template.add_output(Output(
            self.trop_db.title + 'Endpoint',
            Description='Address of the {0} RDS'.format(self.title),
            Value=Join('', [GetAtt(self.trop_db, 'Endpoint.Address'), ':', GetAtt(self.trop_db, 'Endpoint.Port')])))

    def get_dependencies(self):
        """
        :return: returns an empty list as a database has no upstream dependencies
        """
        return self.dependencies

    def get_destinations(self):
        """
        :return: returns a reference to the destination security enabled object of the unit, in this case: itself
        """
        return [self]

    def get_inbound_ports(self):
        """
        :return: returns database port in an array
        """
        return [self.port]

    def add_unit_flow(self, receiver):
        """
        Create security group flow from this Amazonia unit's ASG to another unit's ELB
        :param receiver: Other Amazonia Unit
        """
        raise InvalidFlowError('Error: database_unit {0} may only be the destination of flow, not the originator.'
                               .format(self.title))


class InvalidFlowError(Exception):
    def __init__(self, value):
        self.value = value
