#!/usr/bin/python3
import boto3
import time
import yaml
import argparse
import os
import amazonia.amz as amz

"""
This Script will take a cloud formation template file and upload it to create a cloud formation stack in aws using boto3
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
"""


def read_yaml(user_yaml):
    """
    Ingest user YAML
    :param user_yaml: yaml file location
    :return: Json serialised version of Yaml
    """
    with open(user_yaml, 'r') as stack_yaml:
        return yaml.safe_load(stack_yaml)


def create_template(yaml_data, default_data, schema_data, template_path):
    """
    Creates stack template from amazonia and places it inhte template path
    :param yaml_data: User stack data from application's yaml file
    :param default_data: Default data to be used if not specified in applications yaml file
    :param schema_data: Cerburus schema data used for validation
    :param template_path: path to place template file (inc template file name)
    """
    template_data = amz.generate_template(yaml_data, default_data, schema_data)

    with open(template_path, 'w') as template_file:
        template_file.write(template_data)
        template_file.close()


def upload_s3(s3_client, template_path, s3_bucket, s3_key):
    """
    Upload to s3
    :param s3_client: Boto S3 client API
    :param template_path: Path where output template file was saved to
    :param s3_bucket: S3 bucket where to upload template to
    :param s3_key: Folder and file path key where to upload template to
    """
    s3_client.upload_file(template_path, s3_bucket, s3_key)

    print('File Successfully Uploaded to S3')


def create_and_delete_stack(cf_client, stack_name, s3_bucket, s3_key):
    """
    This Script will take a cloud formation template file and upload it to create a cloud formation stack in aws using boto3
    http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
    :param cf_client: Boto Cloudformation client API
    :param stack_name: name of stack to create and delete
    :param s3_bucket: S3 bucket where to read template from
    :param s3_key: Folder and file path key where to read template from
    """
    template_url = \
        'https://s3-ap-southeast-2.amazonaws.com/' + s3_bucket + '/' + s3_key
    time_delay = 11

    create_response = cf_client.create_stack(
        StackName=stack_name,
        TemplateURL=template_url,
        TimeoutInMinutes=123,
        ResourceTypes=['AWS::*'],
        OnFailure='ROLLBACK',
        Tags=[
            {
                'Key': 'Stack Name',
                'Value': stack_name
            }

        ]
    )

    stack_id = create_response['StackId']
    print('\nStack Creating...\n{0}\n'.format(stack_id))

    # Script to return an AWS Cloudformation Stack_ID or Stack_Name stack status every 10 seconds using boto3.
    # If the status returns CREATE_COMPLETE then exit with success message
    # If the status returns ROLLBACK_IN_PROGRESS or ROLLBACK_COMPLETE then exit with failure message
    # http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks

    while stack_id:
        confirm_response = cf_client.describe_stacks(StackName=stack_id)
        stack_status = confirm_response['Stacks'][0]['StackStatus']

        if stack_status == 'CREATE_COMPLETE':
            print('\nStack Successfully Created...\nStack Status: {0}'.format(stack_status))
            break
        elif stack_status in ('ROLLBACK_IN_PROGRESS', 'ROLLBACK_COMPLETE'):
            print('Error occurred creating AWS CloudFormation stack and returned status code {0}.'.format(stack_status))
            exit(1)
        else:
            print('Stack Status: {0}'.format(stack_status))
        time.sleep(time_delay)

    # This script will delete a stack in AWS
    # http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack

    cf_client.delete_stack(StackName=stack_name)

    print('\nStack {0} Deletion Commencing...\n'.format(stack_name))

    # Script to return an AWS Cloudformation Stack_ID or Stack_Name stack status every 10 seconds using boto3.
    # If the status returns CREATE_COMPLETE then exit with success message
    # If the status returns ROLLBACK_IN_PROGRESS or ROLLBACK_COMPLETE then exit with failure message
    # http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events

    while stack_id:
        confirm_response = cf_client.describe_stacks(StackName=stack_id)
        stack_status = confirm_response['Stacks'][0]['StackStatus']

        if stack_status == 'DELETE_COMPLETE':
            print('\nStack Successfully Deleted...\nStack Status: {0}\n'.format(stack_status))
            break
        elif stack_status in ('ROLLBACK_IN_PROGRESS', 'ROLLBACK_COMPLETE'):
            print('Error occurred creating AWS CloudFormation stack and returned status code {0}.'.format(stack_status))
            exit(1)
        else:
            print('Stack Status: {0}'.format(stack_status))
        time.sleep(time_delay)


def main():
    """
    Accepts arguments
    Reads data
    Creates template
    Uploads template to S3
    Creates and delets stack
    """
    cf_client = boto3.client('cloudformation')
    s3_client = boto3.resource('s3').meta.client

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--yaml',
                        default=os.path.join(__location__, './application.yaml'),
                        help="Path to the applications amazonia yaml file")
    parser.add_argument('-d', '--default',
                        default=os.path.join(__location__, './defaults.yaml'),
                        help='Path to the environmental defaults yaml file')
    parser.add_argument('-s', '--schema',
                        default=os.path.join(__location__, './schema.yaml'),
                        help='Path to the schema to validate the provided yaml values against')
    parser.add_argument('-t', '--template',
                        default='stack.template',
                        help='Path for amazonia to place template file')
    parser.add_argument('-b', '--s3_bucket',
                        default='smallest-bucket-in-history',
                        help='s3 bucket to place template file')
    parser.add_argument('-st', '--stack_name',
                        default='testSysStack',
                        help='Title of stack')
    parser.add_argument('-o', '--out',
                        action='store_true',
                        help='Output template to stdout rather than a file.')
    args = parser.parse_args()

    # YAML ingestion
    yaml_data = read_yaml(args.yaml)
    default_data = read_yaml(args.default)
    schema_data = read_yaml(args.schema)
    template_path = os.path.join(__location__, args.template)
    s3_key = 'amazonia/' + args.template
    s3_bucket = args.s3_bucket
    stack_name = args.stack_name

    # Create template, upload to s3 then create and delete stack
    create_template(yaml_data, default_data, schema_data, template_path)
    upload_s3(s3_client, template_path, s3_bucket, s3_key)
    create_and_delete_stack(cf_client, stack_name, s3_bucket, s3_key)

if __name__ == '__main__':
    main()
