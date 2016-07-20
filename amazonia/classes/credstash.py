#!/usr/bin/python3

from troposphere import Join, Ref, Output
from amazonia.classes.dynamo_db import DynamoDB
from amazonia.classes.kms import KmsKey


class Credstash(object):
    def __init__(self, unit_title, key_title, key_rotation, key_admins, key_users, ddb_title, ddb_att_dict, template):
        """
        CredStash - https://github.com/fugue/credstash
        Create Secret Server using DynamoDB and KMS Key
        :param ddb_title: Name of the DynamoDB Table
        :param ddb_att_dict: Attributes for the DynamoDB object in the format [{ddb_name='name', ddb_atttype='S', ddb_keytype='HASH'},]
        ddb_atttype valid_types = ["S", "N", "B"]
        ddb_keytype valid types = ["HASH", "RANGE"]
        :param key_title: String title of the key in AWS, not the alias name
        :param key_rotation: Boolean to enable or disable key rotation at a cost
        :param key_admins: single string or list of ARNs of IAM objects for apply key admin policy to
        :param key_users: single string or list of ARNs of IAM objects for apply key user policy to
        :param template: The troposphere template to add the DynamoDB troposphere objects to
        """
        self.key_title = unit_title + key_title
        self.ddb_title = unit_title + ddb_title

        self.credstash_key = KmsKey(self.key_title, key_rotation, key_admins, key_users, template)
        self.credstash_ddb = DynamoDB(self.ddb_title, ddb_att_dict, template)

        # Add Output
        template.add_output(Output(
            unit_title,
            Value=Join('', [unit_title,
                            ' is a managed AWS KMS Key and DynamoDB Pair. Key=',
                            Ref(self.credstash_key.k_key),
                            '. DynamoDB=',
                            self.credstash_ddb.ddb_table.TableName,
                            '. Created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName'),
                            ]),
            Description='Amazonia Key and DDB'))

        template.add_output(Output(
            'CredstashPut',
            Value=Join('', ['credstash -r ',
                            Ref('AWS::Region'),
                            ' -t ',
                            self.credstash_ddb.ddb_table.TableName,
                            ' put -k ',
                            Ref(self.credstash_key.k_key),
                            ' -a [credential-name] [credential-secret]'
                            ]),
            Description='Credstash: Put Secret in Credstash Store'))

        template.add_output(Output(
            'CredstashGet',
            Value=Join('', ['credstash -r ',
                            Ref('AWS::Region'),
                            ' -t ',
                            self.credstash_ddb.ddb_table.TableName,
                            ' get -v [credential-version] [credential-name]'
                            ]),
            Description='Credstash: Get Secret from Credstash Store'))
