from troposphere import Template, Ref, Join

from amazonia.classes.dynamo_db import DynamoDB


def main():
    """
    Creates a troposphere template and then adds a single DynamoDB Table
    """
    template = Template()

    DynamoDB(dyndb_title='MyDynamoDB',
             template=template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
