from nose.tools import *
from amazonia.classes.kms import KmsKey
from troposphere import Template

"""
Tests the functions of the KMS class
"""


def test_key_title():
    """
    Test that the key title is correctly set
    """
    template = Template()

    key_names = ['TestKey', 'MyKMSkey', 'Key42']
    for key_name in key_names:
        kms_key = (KmsKey(key_title=key_name,
                          key_rotation=False,
                          key_admins="arn:aws:iam::111122223333:user/admin1",
                          key_users=["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"],
                          template=template))
        assert_equals(kms_key.k_key.title, key_name)


def test_kms_key_policy():
    """
    To test that key policy is applied is passed in
    """
    template = Template()

    key_admins = "arn:aws:iam::111122223333:user/admin1"
    key_users = ["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"]

    kms_key = (KmsKey(key_title='MyTestKey',
                      key_rotation=True,
                      key_admins=key_admins,
                      key_users=key_users,
                      template=template))

    # Test policy is dict
    assert_equals(type(kms_key.k_key.KeyPolicy), dict)

    # TODO assert user in key policy
    # Test user are in policy
    for num, key_admin in enumerate(key_admins):
        admin_dict_key = kms_key.k_key.KeyPolicy['Statement'][0]['Principal']['AWS'][num]
        assert_in(key_admin, admin_dict_key)

    for num, key_user in enumerate(key_users):
        users_dict_key = kms_key.k_key.KeyPolicy['Statement'][1]['Principal']['AWS'][num]
        assert_in(key_user, users_dict_key)


def test_key_rotation():
    """
    Test that the key rotation value is correctly set
    """
    template = Template()

    key_rotations = [True, False]
    for key_rotation in key_rotations:
        kms_key = (KmsKey(key_title='MyKey{0}'.format(key_rotation),
                          key_rotation=key_rotation,
                          key_admins="arn:aws:iam::111122223333:user/admin1",
                          key_users=["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"],
                          template=template))
        key_rotation_state = 'true' if key_rotation is True else 'false'
        assert_equals(kms_key.k_key.EnableKeyRotation, key_rotation_state)
