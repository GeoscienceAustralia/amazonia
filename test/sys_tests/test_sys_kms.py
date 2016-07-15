from troposphere import Template, Ref, Join

from amazonia.classes.kms import KmsKey


def main():
    """
    Creates a troposphere template and then adds a single KMS Key
    """
    template = Template()

    KmsKey(key_title='MyTestKey',
           key_rotation=True,
           key_admins=Join('', ['arn:aws:iam::', Ref('AWS::AccountId'), ':user/admin1']),
           key_users=[Join('', ['arn:aws:iam::', Ref('AWS::AccountId'), ':user/user1']),
                      Join('', ['arn:aws:iam::', Ref('AWS::AccountId'), ':user/user2'])],
           template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
