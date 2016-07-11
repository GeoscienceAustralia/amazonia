#!/usr/bin/python3

from troposphere import Output, Join, Ref
from troposphere.kms import Key


class KmsKey(object):
    def __init__(self, key_title, key_rotation, key_admins, key_users, template):
        """
        AWS - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kms-key.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/kms.py
        """

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

        self.k_key = template.add_resource(Key(key_title,
                                               Description=Join('', [key_title,
                                                                     ' on Stack: ',
                                                                     Ref('AWS::StackName')]),
                                               Enabled=True,
                                               EnableKeyRotation=key_rotation,
                                               KeyPolicy=k_key_policy))
