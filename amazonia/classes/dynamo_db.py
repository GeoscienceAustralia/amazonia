#!/usr/bin/python3


from troposphere.dynamodb2 import Table, ProvisionedThroughput, AttributeDefinition, KeySchema, \
    attribute_type_validator, key_type_validator


class DynamoDB(object):
    def __init__(self, dyndb_title, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/dynamodb2.py
        Create a NoSQL AWS DynamoDB table as a troposphere object
        :param
        """
        # Create Table Resource
        self.dyndb_table = template.add_resource(Table(dyndb_title,
                                                       TableName=dyndb_title,
                                                       AttributeDefinitions=[AttributeDefinition(AttributeName='name',
                                                                                                 AttributeType=attribute_type_validator('S')),
                                                                             AttributeDefinition(AttributeName='version',
                                                                                                 AttributeType=attribute_type_validator('S'))],
                                                       KeySchema=[KeySchema(AttributeName='name',
                                                                            KeyType=key_type_validator('HASH')),
                                                                  KeySchema(AttributeName='version',
                                                                            KeyType=key_type_validator('RANGE'))],
                                                       ProvisionedThroughput=ProvisionedThroughput(ReadCapacityUnits=1,
                                                                                                   WriteCapacityUnits=1)
                                                       ))

