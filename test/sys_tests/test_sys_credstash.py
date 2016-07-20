from troposphere import Template

from amazonia.classes.credstash import Credstash


def main():
    """
    Creates a troposphere template and then adds a KMS Key and DynamoDB table into it
    """
    template = Template()

    Credstash(unit_title='Credstash1',
              key_title='TestCredstashKey',
              key_rotation=False,
              key_admins="arn:aws:iam::111122223333:user/admin1",
              key_users=["arn:aws:iam::111122223333:user/user1", "arn:aws:iam::444455556666:user/user2"],
              ddb_title='MyCredstashDDB',
              ddb_att_dict={},
              template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
