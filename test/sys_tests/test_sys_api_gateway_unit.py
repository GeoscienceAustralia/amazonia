#!/usr/bin/python3

from amazonia.classes.amz_api_gateway import ApiGatewayUnit
from amazonia.classes.amz_lambda import LambdaUnit
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.lambda_config import LambdaConfig
from network_setup import get_network_config


def main():
    network_config, template = get_network_config()

    apiname = 'apigw1'
    methodname = 'login'
    lambda_title = 'MyLambda'
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

    LambdaUnit(
        unit_title=lambda_title,
        template=template,
        dependencies=[],
        stack_config=network_config,
        lambda_config=lambda_config
    )

    ApiGatewayUnit(unit_title=apiname,
                   template=template,
                   method_config=[method_config],
                   stack_config=network_config)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
