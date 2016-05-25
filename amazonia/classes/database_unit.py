#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, rds, Join, Output, GetAtt, Parameter


class DatabaseUnit(SecurityEnabledObject):
    def __init__(self, unit_title, vpc, template, subnets, db_instance_type, db_engine, db_port):
        """ Class to create an RDS and DB subnet group in a vpc
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/rds.py
        :param unit_title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param template: Troposphere stack to append resources to
        :param subnets: subnets to create autoscaled instances in
        :param db_instance_type: Size of the RDS instance
        :param db_engine: DB engine type (Postgres, Oracle, MySQL, etc)
        :param db_port: Port of RDS instance
        """
        self.title = unit_title + 'Rds'
        self.dependencies = []
        self.db_subnet_group_title = unit_title + "Dsg"
        self.port = db_port
        super(DatabaseUnit, self).__init__(vpc=vpc, title=self.title, template=template)

        self.trop_db_subnet_group = template.add_resource(
            rds.DBSubnetGroup(self.db_subnet_group_title,
                              DBSubnetGroupDescription=self.db_subnet_group_title,
                              SubnetIds=[Ref(x) for x in subnets],
                              Tags=Tags(Name=self.db_subnet_group_title)))

        self.username = self.template.add_parameter(Parameter(
            self.title+'Username', Type='String', Description='Master username of {0} RDS'.format(self.title),
            NoEcho=True))

        self.password = self.template.add_parameter(Parameter(
            self.title+'Password', Type='String', Description='Master password of {0} RDS'.format(self.title),
            NoEcho=True))

        self.trop_db = template.add_resource(
            rds.DBInstance(self.title,
                           AllocatedStorage=5,
                           AllowMajorVersionUpgrade=True,
                           AutoMinorVersionUpgrade=True,
                           MultiAZ=True,
                           DBInstanceClass=db_instance_type,
                           DBSubnetGroupName=Ref(self.trop_db_subnet_group),
                           Engine=db_engine,
                           MasterUsername=Ref(self.username),
                           MasterUserPassword=Ref(self.password),
                           Port=self.port,
                           VPCSecurityGroups=[Ref(self.security_group)],
                           Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', self.title]))))

        self.template.add_output(Output(
            self.trop_db.title+'Address',
            Description='Address of the {0} RDS'.format(self.title),
            Value=GetAtt(self.trop_db, 'Endpoint.Address')))

        self.template.add_output(Output(
            self.trop_db.title+'Port',
            Description='Port of the {0} RDS'.format(self.title),
            Value=GetAtt(self.trop_db, 'Endpoint.Port')))

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
        raise InvalidFlowError("Error: database_unit {0} may only be the destination of flow, not the originator."
                               .format(self.title))


class InvalidFlowError(Exception):
    def __init__(self, value):
        self.value = value
