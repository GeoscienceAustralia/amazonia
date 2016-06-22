from troposphere import Template

from amazonia.classes.s3 import S3


def main():
    template = Template()

    S3(unit_title='MyBucket',
       template=template,
       s3_access='PublicRead'
       )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
