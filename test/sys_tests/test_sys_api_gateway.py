#!/usr/bin/python3

from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_unit import ApiGatewayUnit
from troposphere import Template


def main():
    template = Template()
    apiname = 'test'
    methodname = 'login'
    lambda_unit = 'testlambda'
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
                                           lambda_unit=lambda_unit,
                                           request_config=request_config,
                                           response_config=[response_config1, response_config2],
                                           httpmethod=httpmethod,
                                           authorizationtype=authorizationtype)
    ApiGatewayUnit(unit_title=apiname,
                   template=template,
                   method_config=[method_config],
                   network_config=None)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
