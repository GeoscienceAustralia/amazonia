#!/usr/bin/python3


from troposphere.dynamodb2 import Table, ProvisionedThroughput, AttributeDefinition, KeySchema, \
    attribute_type_validator, key_type_validator


class DynamoDB(object):
    def __init__(self, ddb_title, ddb_att_dict, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/dynamodb2.py
        Create a NoSQL AWS DynamoDB table as a troposphere object
        :param ddb_title: Name of the DynamoDB Table, must be Alphanumeric
        :param ddb_att_dict: Attributes for the DynamoDB object in the format [{ddb_name='name', ddb_atttype='S', ddb_keytype='HASH'},]
        ddb_atttype valid_types = ["S", "N", "B"]
        ddb_keytype valid types = ["HASH", "RANGE"]
        :param template: The troposphere template to add the DynamoDB troposphere objects to
        """
        self.attribute_definitions = []
        self.key_schema = []

        for ddb_att in ddb_att_dict:
            self.attribute_definitions.append(AttributeDefinition(AttributeName=ddb_att['ddb_name'],
                                                                  AttributeType=attribute_type_validator(ddb_att['ddb_atttype'])))
            self.key_schema.append(KeySchema(AttributeName=ddb_att['ddb_name'],
                                             KeyType=key_type_validator(ddb_att['ddb_keytype'])))

        # Create Table Resource
        self.ddb_table = template.add_resource(Table(ddb_title,
                                                     TableName=ddb_title,
                                                     AttributeDefinitions=self.attribute_definitions,
                                                     KeySchema=self.key_schema,
                                                     ProvisionedThroughput=ProvisionedThroughput(ReadCapacityUnits=1,
                                                                                                 WriteCapacityUnits=1)))


