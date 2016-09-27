#!/usr/bin/python3

from amazonia.classes.amz_lambda import LambdaUnit
from amazonia.classes.lambda_config import LambdaConfig
from network_setup import get_network_config


def main():
    network_config, template = get_network_config()

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
    LambdaUnit(unit_title='MyLambda',
               stack_config=network_config,
               template=template,
               dependencies=[],
               lambda_config=lambda_config
               )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
