from amazonia.classes.amz_lambda import LambdaUnit, LambdaLeaf
from amazonia.classes.lambda_config import LambdaConfig, InvalidLambdaConfigError
from network_setup import get_network_config
from nose.tools import *
from troposphere import Join

template = network_config = lambda_config = availability_zones = public_cidr = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, lambda_config, availability_zones, public_cidr

    network_config, template = get_network_config()
    availability_zones = ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']
    public_cidr = {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}

    lambda_config = LambdaConfig(
        lambda_s3_bucket='bucket_name',
        lambda_s3_key='key_name',
        lambda_description='blah',
        lambda_function_name='my_function',
        lambda_handler='main',
        lambda_memory_size=128,
        lambda_role_arn='test_arn',
        lambda_runtime='python2.7',
        lambda_timeout=1,
        lambda_schedule='cron(0/5 * * * ? *)'
    )


def test_invalid_lambda_memory_size():
    assert_raises(InvalidLambdaConfigError, LambdaConfig, **{
        'lambda_memory_size': 129,
        'lambda_s3_bucket': 'bucket_name',
        'lambda_s3_key': 'key_name',
        'lambda_description': 'blah',
        'lambda_function_name': 'my_function',
        'lambda_handler': 'main',
        'lambda_role_arn': 'test_arn',
        'lambda_runtime': 'python2.7',
        'lambda_timeout': 1,
        'lambda_schedule': 'cron(0/5 * * * ? *)'
    })


@with_setup(setup_resources)
def test_lambda_unit():
    """ Tests correct structure of lambda unit.
    """
    my_lambda = LambdaUnit(unit_title='MyLambda',
                           stack_config=network_config,
                           template=template,
                           dependencies=['MyDb:5432'],
                           lambda_config=lambda_config
                           )
    assert_equals(my_lambda.trop_lambda_function.Code.S3Bucket, 'bucket_name')
    assert_equals(my_lambda.trop_lambda_function.Code.S3Key, 'key_name')
    assert_equals(my_lambda.trop_lambda_function.Description, 'blah')
    assert_is(type(my_lambda.trop_lambda_function.FunctionName), Join)
    assert_equals(my_lambda.trop_lambda_function.Handler, 'main')
    assert_equals(my_lambda.trop_lambda_function.MemorySize, 128)
    assert_equals(my_lambda.trop_lambda_function.Role, 'test_arn')
    assert_equals(my_lambda.trop_lambda_function.Runtime, 'python2.7')
    assert_equals(my_lambda.trop_lambda_function.Timeout, 1)
    assert_equals(my_lambda.trop_cw_rule.ScheduleExpression, 'cron(0/5 * * * ? *)')
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SubnetIds), 3)
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SecurityGroupIds), 1)


@with_setup(setup_resources)
def test_lambda_leaf():
    """ Tests correct structure of lambda leaf.
    """
    my_lambda = LambdaLeaf(leaf_title='MyLambda',
                           tree_name='testtree',
                           template=template,
                           dependencies=['MyDb:5432'],
                           lambda_config=lambda_config,
                           availability_zones=availability_zones,
                           public_cidr=public_cidr
                           )
    assert_equals(my_lambda.trop_lambda_function.Code.S3Bucket, 'bucket_name')
    assert_equals(my_lambda.trop_lambda_function.Code.S3Key, 'key_name')
    assert_equals(my_lambda.trop_lambda_function.Description, 'blah')
    assert_is(type(my_lambda.trop_lambda_function.FunctionName), Join)
    assert_equals(my_lambda.trop_lambda_function.Handler, 'main')
    assert_equals(my_lambda.trop_lambda_function.MemorySize, 128)
    assert_equals(my_lambda.trop_lambda_function.Role, 'test_arn')
    assert_equals(my_lambda.trop_lambda_function.Runtime, 'python2.7')
    assert_equals(my_lambda.trop_lambda_function.Timeout, 1)
    assert_equals(my_lambda.trop_cw_rule.ScheduleExpression, 'cron(0/5 * * * ? *)')
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SubnetIds), 3)
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SecurityGroupIds), 1)
