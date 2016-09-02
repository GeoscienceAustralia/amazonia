from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway import ApiGateway
from troposphere import Template, Ref, Join, GetAtt
from nose.tools import *


template = apiname = methodname = lambda_arn = httpmethod = authorizationtype = request_template = request_parameters =\
    response_template = response_parameters = response_models = statuscode = None


def setup_resources():
    global template, apiname, methodname, lambda_arn, httpmethod, authorizationtype, request_template,\
        request_parameters, response_template, response_parameters, response_models, statuscode

    template = Template()
    apiname = 'test0'
    methodname = 'login0'
    lambda_arn = 'arn:aws:lambda:ap-southeast-2:123456789:function:test'
    httpmethod = 'POST'
    authorizationtype = 'NONE'

    request_template = {'application/json': """{ "username": $input.json('$.username')}"""}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-COokie': 'integration.response.body.TESTVALUE'}
    response_models = {'application/json': 'Empty'}
    statuscode = '200'


@with_setup(setup_resources())
def test_request_config():
    """
    Tests the creation of a request config
    """
    request = create_request_config()

    assert_equals(request.templates, request_template)
    assert_equals(request.parameters, request_parameters)


@with_setup(setup_resources())
def test_response_config():
    """
    Tests the creation of a response config
    """
    response = create_response_config()

    assert_equals(response.templates, response_template)
    assert_equals(response.parameters, response_parameters)
    assert_equals(response.statuscode, statuscode)
    assert_equals(response.models, response_models)


@with_setup(setup_resources())
def test_method_config():
    """
    Tests the creation of a method config
    """
    request = create_request_config()
    response = create_response_config()

    method = create_method_config(request, [response])

    assert_equals(method.method_name, methodname)
    assert_equals(method.lambda_arn, lambda_arn)
    assert_equals(method.request, request)
    assert_equals(method.responses, [response])
    assert_equals(method.httpmethod, httpmethod)
    assert_equals(method.authorizationtype, authorizationtype)


@with_setup(setup_resources())
def test_creation_of_api():
    """
    Tests the creation of an api
    """
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)

    assert_equals(api.title, apiname)
    assert_equals(api.api.title, '{0}API'.format(apiname))
    assert_equals(api.api.Name, apiname)


@with_setup(setup_resources())
def test_creation_of_method():
    """
    Tests the creation of a method
    """
    global apiname, methodname
    apiname = 'test1'
    methodname = 'login1'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)

    assert_equals(len(api.methods), 1)
    assert_equals(api.methods[0].title, '{0}Method'.format(methodname))
    assert_equals(type(api.methods[0].RestApiId), Ref)
    assert_equals(api.methods[0].AuthorizationType, authorizationtype)
    assert_equals(type(api.methods[0].ResourceId), Ref)
    assert_equals(api.methods[0].HttpMethod, httpmethod)
    assert_equals(api.methods[0].RequestParameters, request_parameters)

    method_response = api.methods[0].MethodResponses[0]

    assert_equals(len(api.methods[0].MethodResponses), 1)
    assert_equals(method_response.title, '{0}Response{1}'.format(methodname, 0))
    assert_equals(method_response.StatusCode, statuscode)
    assert_equals(method_response.ResponseModels, response_models)
    assert_equals(method_response.ResponseParameters, response_parameters)


@with_setup(setup_resources())
def test_creation_of_integration():
    """
    Tests the creation of an integration
    """
    global apiname, methodname
    apiname = 'test2'
    methodname = 'login2'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)
    integration = api.methods[0].Integration

    assert_equals(integration.title, '{0}Integration'.format(methodname))
    assert_equals(integration.Credentials, '')
    assert_equals(integration.Type, 'AWS')
    assert_equals(integration.IntegrationHttpMethod, httpmethod)
    assert_equals(len(integration.IntegrationResponses), 1)
    assert_equals(integration.RequestTemplates, request_template)
    assert_equals(type(integration.Uri), Join)

    integration_response = integration.IntegrationResponses[0]
    assert_equals(integration_response.title, '{0}IntegrationResponse{1}'.format(methodname, 0))
    assert_equals(integration_response.StatusCode, statuscode)
    assert_equals(integration_response.ResponseParameters, response_parameters)
    assert_equals(integration_response.ResponseTemplates, response_template)


@with_setup(setup_resources)
def create_request_config():
    """
    Create a request config
    :return: a request config object
    """

    return ApiGatewayRequestConfig(templates=request_template,
                                   parameters=request_parameters)


@with_setup(setup_resources)
def create_response_config():
    """
    Create a response config
    :return: a response config object
    """

    return ApiGatewayResponseConfig(templates=response_template,
                                    parameters=response_parameters,
                                    statuscode=statuscode,
                                    models=response_models)


@with_setup(setup_resources)
def create_method_config(request, responses):
    """
    Creates a method config object, stitching together the request and reponses that are passed in
    :param request: a request config object.
    :param responses: a list of response config objects
    :return: a method config object
    """

    return ApiGatewayMethodConfig(method_name=methodname,
                                  lambda_arn=lambda_arn,
                                  request=request,
                                  responses=responses,
                                  httpmethod=httpmethod,
                                  authorizationtype=authorizationtype)


@with_setup(setup_resources)
def create_api(method_config):
    """
    Creates an API object using a method_config object
    :param method_config: a method config
    :return: an Api gateway object
    """

    return ApiGateway(apiname, template, [method_config])

