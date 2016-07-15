from amazonia.classes.sns import SNS
from troposphere import Template


def main():
    """
    Creates a troposphere template and then adds a single s3 bucket
    """
    template = Template()

    SNS(unit_title='test',
        template=template,
        topic_name='topic_name',
        display_name='display_name')

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
