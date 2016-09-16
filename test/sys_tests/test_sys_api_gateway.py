#!/usr/bin/python3

from amazonia.classes.sns import SNS
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.api_gateway_unit import ApiGatewayUnit
from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.lambda_unit import LambdaUnit
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from troposphere import Template, ec2, Ref, Tags


def main():
    template = Template()
    apiname = 'test'
    methodname = 'login'
    lambda_title = 'testlambda'
    httpmethod = 'POST'
    authorizationtype = 'NONE'

    request_template = {'application/json': """{ "username": $input.json('$.username')}"""}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-COokie': 'integration.response.body.TESTVALUE'}
    response_models = {'application/json': 'Empty'}
    statuscode = '200'
    selectionpattern = ''
    request_config = ApiGatewayRequestConfig(templates=request_template,
                                             parameters=request_parameters)
    response_config1 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=statuscode,
                                                models=response_models,
                                                selectionpattern=selectionpattern)
    statuscode = '403'
    selectionpattern = 'Invalid.*'
    response_config2 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=statuscode,
                                                models=response_models,
                                                selectionpattern=selectionpattern)

    method_config = ApiGatewayMethodConfig(method_name=methodname,
                                           lambda_unit=lambda_title,
                                           request_config=request_config,
                                           response_config=[response_config1, response_config2],
                                           httpmethod=httpmethod,
                                           authorizationtype=authorizationtype)

    vpc = template.add_resource(ec2.VPC('myVpc',
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

    public_subnets = [ec2.Subnet('MySubnet2',
                                 AvailabilityZone='ap-southeast-2a',
                                 VpcId=Ref(vpc),
                                 CidrBlock='10.0.2.0/24')]

    sns_topic = SNS(template)

    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        sns_topic=sns_topic,
        public_hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )

    nat = SingleInstance(title='Nat',
                         template=template,
                         single_instance_config=single_instance_config
                         )

    network_config = NetworkConfig(
        public_cidr=None,
        vpc=vpc,
        public_subnets=None,
        private_subnets=private_subnets,
        jump=None,
        nat=nat,
        public_hosted_zone_name=None,
        private_hosted_zone=None,
        cd_service_role_arn=None,
        keypair=None,
        nat_highly_available=False,
        nat_gateways=None,
        sns_topic=sns_topic
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
        lambda_timeout=1,
        lambda_schedule=None
    )

    lambda_unit = LambdaUnit(
        unit_title=lambda_title,
        template=template,
        dependencies=None,
        network_config=network_config,
        lambda_config=lambda_config
    )

    apigw = ApiGatewayUnit(unit_title=apiname,
                           template=template,
                           method_config=[method_config],
                           network_config=None, deployment_config=None)

    apigw.add_unit_flow(lambda_unit)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
