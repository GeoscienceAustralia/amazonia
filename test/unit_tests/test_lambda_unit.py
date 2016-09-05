from amazonia.classes.lambda_unit import LambdaUnit, InvalidFlowError
from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.network_config import NetworkConfig
from nose.tools import *
from troposphere import ec2, Ref, Tags, Template, Join

template = network_config = lambda_config = None


def setup_resources():
    """ Setup global variables between tests"""
    global template, network_config, lambda_config

    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc),
                                                   DependsOn=internet_gateway.title))

    private_subnets = [template.add_resource(ec2.Subnet('MyPrivSub1',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub2',
                                                        AvailabilityZone='ap-southeast-2b',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.2.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub3',
                                                        AvailabilityZone='ap-southeast-2c',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.3.0/24'))]
    network_config = NetworkConfig(
        public_cidr=None,
        vpc=vpc,
        public_subnets=None,
        private_subnets=private_subnets,
        jump=None,
        nat=None,
        stack_hosted_zone_name=None,
        cd_service_role_arn=None,
        keypair=None,
        nat_highly_available=False,
        nat_gateways=None
    )

    lambda_config = LambdaConfig(
        lambda_s3_bucket='bucket_name',
        lambda_s3_key='key_name',
        lambda_description='blah',
        lambda_function_name='my_function',
        lambda_handler='main',
        lambda_memory_size=128,
        lambda_role_arn='test_arn',
        lambda_runtime='python2.7',
        lambda_timeout=1
    )


@with_setup(setup_resources)
def test_lambda():
    """ Tests correct structure of lambda unit.
    """
    global network_config, lambda_config, template

    my_lambda = LambdaUnit(unit_title='MyLambda',
                           network_config=network_config,
                           template=template,
                           dependencies=[],
                           lambda_config=lambda_config
                           )
    assert_equals(my_lambda.trop_lambda_function.Code.S3Bucket, 'bucket_name')
    assert_equals(my_lambda.trop_lambda_function.Code.S3Key, 'key_name')
    assert_equals(my_lambda.trop_lambda_function.Description, 'blah')
    assert_equals(my_lambda.trop_lambda_function.FunctionName, 'my_function')
    assert_equals(my_lambda.trop_lambda_function.Handler, 'main')
    assert_equals(my_lambda.trop_lambda_function.MemorySize, 128)
    assert_equals(my_lambda.trop_lambda_function.Role, 'test_arn')
    assert_equals(my_lambda.trop_lambda_function.Runtime, 'python2.7')
    assert_equals(my_lambda.trop_lambda_function.Timeout, 1)
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SubnetIds), 3)
    assert_equals(len(my_lambda.trop_lambda_function.VpcConfig.SecurityGroupIds), 1)
    assert_raises(InvalidFlowError, my_lambda.add_unit_flow, **{'receiver': my_lambda})
