#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, rds, Join, Output, GetAtt, Parameter


class DatabaseUnit(SecurityEnabledObject):
    def __init__(self, unit_title, vpc, template, subnets, db_hdd_size, db_instance_type, db_engine, db_port, db_name,
                 db_snapshot_id):
        """
        Class to create an RDS and DB subnet group in a vpc
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/rds.py
        :param unit_title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param template: Troposphere stack to append resources to
        :param subnets: subnets to create autoscaled instances in
        :param db_snapshot_id: id of snapshot to restore from
        :param db_hdd_size: allocated storage size
        :param db_name: the specific name of the database to be created
        :param db_instance_type: Size of the RDS instance
        :param db_engine: DB engine type (Postgres, Oracle, MySQL, etc)
        :param db_port: Port of RDS instance
        """
        self.title = unit_title + 'Rds'
        self.dependencies = []
        self.db_subnet_group_title = unit_title + 'Dsg'
        self.port = db_port
        super(DatabaseUnit, self).__init__(vpc=vpc, title=self.title, template=template)

        self.trop_db_subnet_group = template.add_resource(
            rds.DBSubnetGroup(self.db_subnet_group_title,
                              DBSubnetGroupDescription=self.db_subnet_group_title,
                              SubnetIds=[Ref(x) for x in subnets],
                              Tags=Tags(Name=self.db_subnet_group_title)))
        rds_params = {
            'AllocatedStorage': db_hdd_size,
            'AllowMajorVersionUpgrade': True,
            'AutoMinorVersionUpgrade': True,
            'MultiAZ': True,
            'DBInstanceClass': db_instance_type,
            'DBSubnetGroupName': Ref(self.trop_db_subnet_group),
            'DBName': db_name,
            'Engine': db_engine,
            'Port': self.port,
            'VPCSecurityGroups': [Ref(self.security_group)],
            'Tags': Tags(Name=Join('', [Ref('AWS::StackName'), '-', self.title]))
        }
        if db_snapshot_id is None:
            self.username = self.template.add_parameter(Parameter(
                self.title + 'Username', Type='String', Description='Master username of {0} RDS'.format(self.title),
                NoEcho=True))

            self.password = self.template.add_parameter(Parameter(
                self.title + 'Password', Type='String', Description='Master password of {0} RDS'.format(self.title),
                NoEcho=True))
            rds_params['MasterUsername'] = Ref(self.username)
            rds_params['MasterUserPassword'] = Ref(self.password)
        else:
            rds_params['DBSnapshotIdentifier'] = db_snapshot_id
            rds_params['DBName'] = ''

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

    def get_destination(self):
        """
        :return: returns a reference to the destination security enabled object of the unit, in this case: itself
        """
        return self

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
