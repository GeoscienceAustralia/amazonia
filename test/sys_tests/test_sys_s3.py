from troposphere import Template

from amazonia.classes.s3 import S3


def main():
    """
    Creates a troposphere template and then adds a single s3 bucket
    """
    template = Template()

    S3(unit_title='MyBucket',
       template=template,
       s3_access='PublicRead',
       bucket_policy='')

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
