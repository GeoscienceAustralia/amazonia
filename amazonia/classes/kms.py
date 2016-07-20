#!/usr/bin/python3

from troposphere import Join, Ref, Output
from troposphere.kms import Key


class KmsKey(object):
    def __init__(self, key_title, key_rotation, key_admins, key_users, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/kms.py
        Create a Customer Master key in KMS for encrpytion and use with credstash
        :param key_title: String title of the key in AWS, not the alias name, must be alphanumeric
        :param key_rotation: Boolean to enable or disable key rotation at a cost
        :param key_admins: single string or list of ARNs of IAM objects for apply key admin policy to
        :param key_users: single string or list of ARNs of IAM objects for apply key user policy to
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        """
        # Policy for Admins and users
        k_key_policy = {
            "Version": "2012-10-17",
            "Id": "key-default-1",
            "Statement": [
                {
                    "Sid": "Allow administration of the key",
                    "Effect": "Allow",
                    "Principal": {"AWS": key_admins},
                    "Action": [
                        "kms:Create*",
                        "kms:Describe*",
                        "kms:Enable*",
                        "kms:List*",
                        "kms:Put*",
                        "kms:Update*",
                        "kms:Revoke*",
                        "kms:Disable*",
                        "kms:Get*",
                        "kms:Delete*",
                        "kms:ScheduleKeyDeletion",
                        "kms:CancelKeyDeletion"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "Allow use of the key",
                    "Effect": "Allow",
                    "Principal": {"AWS": key_users},
                    "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:ReEncrypt",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey"
                    ],
                    "Resource": "*"
                }
            ]
        }

        # Create Key Resource
        self.k_key = template.add_resource(Key(key_title,
                                               Description=Join('', [key_title,
                                                                     ' on Stack: ',
                                                                     Ref('AWS::StackName')]),
                                               Enabled=True,
                                               EnableKeyRotation=key_rotation,
                                               KeyPolicy=k_key_policy))

        # Add Output
        template.add_output(Output(
            key_title,
            Value=Join('', [Ref(self.k_key),
                            ' is a managed AWS KMS Key and Key Rotation = ',
                            self.k_key.EnableKeyRotation.upper(),
                            '. Created with Amazonia as part of stack name - ',
                            Ref('AWS::StackName'),
                            ]),
            Description='Amazonia KMS Key Bucket'
        ))
