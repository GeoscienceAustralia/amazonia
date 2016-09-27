#!/usr/bin/python3

from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.amz_lambda import LambdaLeaf
from troposphere import Template


def main():
    template = Template()

    lambda_config = LambdaConfig(
        lambda_s3_bucket='smallest-bucket-in-history',
        lambda_s3_key='test_lambda.zip',
        lambda_description='test function',
        lambda_function_name='test_lambda',
        lambda_handler='test_lambda.lambda_handler',
        lambda_memory_size=128,
        lambda_role_arn='arn:aws:iam::123456789:role/lambda_basic_vpc_execution_with_s3',
        lambda_runtime='python2.7',
        lambda_timeout=1,
        lambda_schedule='rate(5 minutes)'
    )

    # Test Lambda
    LambdaLeaf(leaf_title='MyLambda',
               template=template,
               dependencies=['app1:80'],
               lambda_config=lambda_config,
               availability_zones=['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c'],
               public_cidr={'name': 'PublicIp', 'cidr': '0.0.0.0/0'},
               tree_name='tree'
               )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
