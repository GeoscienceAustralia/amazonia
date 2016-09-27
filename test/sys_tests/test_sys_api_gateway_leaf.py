#!/usr/bin/python3

from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig, ApiGatewayResponseConfig, \
    ApiGatewayRequestConfig
from amazonia.classes.amz_api_gateway import ApiGatewayLeaf
from troposphere import Template


def main():
    template = Template()
    api_name = 'apigw1'
    method_name = 'login'
    lambda_title = 'MyLambda'
    http_method = 'POST'
    authorization_type = 'NONE'

    request_template = {'application/json': """{ "username": $input.json('$.username')}"""}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-COokie': 'integration.response.body.TESTVALUE'}
    response_models = {'application/json': 'Empty'}
    status_code = '200'
    selection_pattern = ''
    request_config = ApiGatewayRequestConfig(templates=request_template,
                                             parameters=request_parameters)
    response_config1 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=status_code,
                                                models=response_models,
                                                selectionpattern=selection_pattern)
    status_code = '403'
    selection_pattern = 'Invalid.*'
    response_config2 = ApiGatewayResponseConfig(templates=response_template,
                                                parameters=response_parameters,
                                                statuscode=status_code,
                                                models=response_models,
                                                selectionpattern=selection_pattern)

    method_config = ApiGatewayMethodConfig(method_name=method_name,
                                           lambda_unit=lambda_title,
                                           request_config=request_config,
                                           response_config=[response_config1, response_config2],
                                           httpmethod=http_method,
                                           authorizationtype=authorization_type)

    ApiGatewayLeaf(leaf_title=api_name,
                   template=template,
                   method_config=[method_config],
                   tree_name='tree')

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
