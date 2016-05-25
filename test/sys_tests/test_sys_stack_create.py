#!/usr/bin/python3
import boto3
import time
import amazonia.amz as amz

"""
This Script will take a cloud formation template file and upload it to create a cloud formation stack in aws using boto3
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
"""
cf_client = boto3.client('cloudformation')
s3_client = boto3.resource('s3').meta.client

template = amz.main()

s3_response = s3_client.upload_file('stack.template', 'smallest-bucket-in-history',
                                    'smallest_app_in_history/stack.template')

print('File Successfully Uploaded to S3')

stack_name = 'teststack'
template_url = \
    'https://s3-ap-southeast-2.amazonaws.com/smallest-bucket-in-history/smallest_app_in_history/stack.template'
environment = 'test'
app = 'app1'
infra_code_version = '0.3'
tags = {'Key': 'TestTag', 'Value': 'Testvalue'}
time_delay = 11

"""
This Script will take a cloud formation template file and upload it to create a cloud formation stack in aws using boto3
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
"""

create_response = cf_client.create_stack(
    StackName=stack_name,
    TemplateURL=template_url,
    TimeoutInMinutes=123,
    ResourceTypes=['AWS::*'],
    OnFailure='ROLLBACK',
    Tags=[
        {
            'Key': 'Environment',
            'Value': environment
        },
        {
            'Key': 'Application',
            'Value': app
        },
        {
            'Key': 'Infra_Code_Version',
            'Value': infra_code_version
        },
        tags,

    ]
)

stack_id = create_response['StackId']
print('\nStack Creating...\n{0}\n'.format(stack_id))


"""
Script to return an AWS Cloudformation Stack_ID or Stack_Name stack status every 10 seconds using boto3.
If the status returns CREATE_COMPLETE then exit with success message
If the status returns ROLLBACK_IN_PROGRESS or ROLLBACK_COMPLETE then exit with failure message
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
"""
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

"""
This script will delete a stack in AWS
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack
"""
delete_response = cf_client.delete_stack(StackName=stack_name)

print('\nStack {0} Deletion Commencing...\n'.format(stack_name))

"""
Script to return an AWS Cloudformation Stack_ID or Stack_Name stack status every 10 seconds using boto3.
If the status returns CREATE_COMPLETE then exit with success message
If the status returns ROLLBACK_IN_PROGRESS or ROLLBACK_COMPLETE then exit with failure message
http://boto3.readthedocs.org/en/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events
"""
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
