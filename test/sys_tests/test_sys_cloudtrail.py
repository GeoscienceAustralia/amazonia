from troposphere import Template

from amazonia.classes.cloudtrail import Cloudtrail


def main():
    """
    Creates a troposphere template and then adds a single s3 bucket and assocaited cloud trail
    """
    template = Template()

    Cloudtrail('MyCloud', template)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
