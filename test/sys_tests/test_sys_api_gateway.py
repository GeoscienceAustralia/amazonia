#!/usr/bin/python3

from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway import ApiGateway
from troposphere import Template


def main():
    template = Template()
    apiname = 'test'
    methodname = 'login'
    lambda_arn = 'arn:aws:lambda:ap-southeast-2:123456789:function:test'
    httpmethod = 'POST'
    authorizationtype = 'NONE'

    request_template = {'application/json': '{ "username": $input.json(\'$.username\'),\
 "password": $input.json(\'$.password\'),\
 "origin": "$input.params(\'Origin\')",\
 "context": {\
    "source-ip": "$context.identity.sourceIp",\
    "user-agent": "$context.identity.userAgent"\
 }\
}'}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-COokie': 'integration.response.body.JSESSIONID',
                           'method.response.header.Access-Control-Allow-Origin': '\'http://sentinel-secure.gadevs.ga\'',
                           'method.response.header.Set-Cookie': 'integration.response.body.CloudFrontKeyPairId',
                           'method.response.header.Set-CoOkie': 'integration.response.body.AWSELB',
                           'method.response.header.SEt-Cookie': 'integration.response.body.CloudFrontSignature',
                           'method.response.header.SeT-Cookie': 'integration.response.body.CloudFrontPolicy'}
    response_models = {'application/json': 'Empty'}
    statuscode = '200'
    request_config = ApiGatewayRequestConfig(request_template, request_parameters)
    response_config1 = ApiGatewayResponseConfig(response_template, response_parameters, statuscode, response_models)
    statuscode = '403'
    response_config2 = ApiGatewayResponseConfig(response_template, response_parameters, statuscode, response_models)
    method_config = ApiGatewayMethodConfig(method_name=methodname,
                                           lambda_arn=lambda_arn,
                                           request=request_config,
                                           responses=[response_config1, response_config2],
                                           httpmethod=httpmethod,
                                           authorizationtype=authorizationtype)
    ApiGateway(apiname, template, [method_config])

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
