from troposphere import Template

from amazonia.classes.dynamo_db import DynamoDB


def main():
    """
    Creates a troposphere template and then adds a single DynamoDB Table
    """
    template = Template()

    DynamoDB(ddb_title='MyDynamoDB',
             ddb_att_dict=[{'ddb_name': 'Name', 'ddb_atttype': 'S', 'ddb_keytype': 'HASH'},
                           {'ddb_name': 'Version', 'ddb_atttype': 'S', 'ddb_keytype': 'RANGE'}],
             template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
