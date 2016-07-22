from amazonia.classes.credstash import Credstash
from troposphere import Template

"""
Tests the functions of the Credstash class
"""


def test_kms_key():
    """
    Test that the kms key is correctly created
    """
    template = Template()

    credstash = Credstash(unit_title='credstash1',
                          key_title='TestCredstashKey',
                          key_rotation=False,
                          key_admins="arn:aws:iam::111122223333:user/admin1",
                          key_users=["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"],
                          ddb_title='MyCredstashDDB',
                          ddb_att_dict={},
                          template=template)

    assert credstash.credstash_key.k_key


def test_dynamodb():
    """
    To test that dynamodb is being correctly created
    """
    template = Template()

    credstash = Credstash(unit_title='credstash1',
                          key_title='TestCredstashKey',
                          key_rotation=False,
                          key_admins="arn:aws:iam::111122223333:user/admin1",
                          key_users=["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"],
                          ddb_title='MyCredstashDDB',
                          ddb_att_dict={},
                          template=template)

    assert credstash.credstash_ddb.ddb_table
