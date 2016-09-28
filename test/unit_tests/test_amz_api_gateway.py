from amazonia.classes.amz_api_gateway import ApiGatewayLeaf
from amazonia.classes.amz_api_gateway import ApiGatewayUnit
from amazonia.classes.amz_lambda import LambdaUnit
from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.lambda_config import LambdaConfig
from network_setup import get_network_config
from nose.tools import *
from troposphere import Ref, Join

template = apiname = methodname = httpmethod = authorizationtype = request_template = request_parameters = \
    response_template = response_parameters = response_models = selection_pattern = statuscode = lambda_title = \
    network_config = tree_name = None


def setup_resources():
    """
    Initialise resources before each test
    """
    global template, network_config, apiname, methodname, httpmethod, authorizationtype, request_template, \
        lambda_title, request_parameters, response_template, response_parameters, response_models, selection_pattern, \
        statuscode, tree_name
    tree_name = 'testtree'
    network_config, template = get_network_config()
    apiname = 'test0'
    methodname = 'login0'
    httpmethod = 'POST'
    authorizationtype = 'NONE'
    lambda_title = 'lambdatest1'
    request_template = {'application/json': """{ "username": $input.json('$.username')}"""}
    request_parameters = {'method.request.header.Origin': "$input.params('Origin')"}
    response_template = {'application/json': ''}
    response_parameters = {'method.response.header.Set-Cookie': 'integration.response.body.TESTVALUE'}
    response_models = {'application/json': 'Empty'}
    statuscode = '200'
    selection_pattern = ''


@with_setup(setup_resources)
def test_request_config():
    """
    Tests the creation of a request config
    """
    request = create_request_config()

    assert_equals(request.templates, request_template)
    assert_equals(request.parameters, request_parameters)


@with_setup(setup_resources)
def test_response_config():
    """
    Tests the creation of a response config
    """
    response = create_response_config()

    assert_equals(response.templates, response_template)
    assert_equals(response.parameters, response_parameters)
    assert_equals(response.selectionpattern, selection_pattern)
    assert_equals(response.statuscode, statuscode)
    assert_equals(response.models, response_models)


@with_setup(setup_resources)
def test_method_config():
    """
    Tests the creation of a method config
    """
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])

    assert_equals(method.method_name, methodname)
    assert_equals(method.lambda_unit, lambda_title)
    assert_equals(method.request, request)
    assert_equals(method.responses, [response])
    assert_equals(method.httpmethod, httpmethod)
    assert_equals(method.authorizationtype, authorizationtype)


@with_setup(setup_resources)
def test_creation_of_api_leaf():
    """
    Tests the creation of an api unit and api leaf
    """
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api_leaf = create_api_leaf(method)

    assert_equals(api_leaf.title, apiname)
    assert_equals(api_leaf.api.title, apiname)
    assert_equals(api_leaf.tree_name, tree_name)


@with_setup(setup_resources)
def test_creation_of_api_unit():
    """
    Tests the creation of an api unit and api leaf
    """
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api_unit = create_api_unit(method)

    assert_equals(api_unit.title, apiname)
    assert_equals(api_unit.api.title, apiname)


@with_setup(setup_resources)
def test_creation_of_method():
    """
    Tests the creation of a method
    """
    global apiname, methodname, lambda_title
    apiname = 'test1'
    methodname = 'login1'
    lambda_title += '1'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api_unit(method)
    add_lambda('1')

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


@with_setup(setup_resources)
def test_creation_of_integration():
    """
    Tests the creation of an integration
    """
    global apiname, methodname, lambda_title
    apiname = 'test2'
    methodname = 'login2'
    lambda_title += '2'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api_unit(method)
    add_lambda('2')

    integration = api.methods[0].Integration

    assert_equals(integration.title, '{0}Integration'.format(methodname))
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


def create_request_config():
    """
    Create a request config
    :return: a request config object
    """

    return ApiGatewayRequestConfig(templates=request_template,
                                   parameters=request_parameters)


def create_response_config():
    """
    Create a response config
    :return: a response config object
    """

    return ApiGatewayResponseConfig(templates=response_template,
                                    parameters=response_parameters,
                                    selectionpattern=selection_pattern,
                                    statuscode=statuscode,
                                    models=response_models)


def create_method_config(request, responses):
    """
    Creates a method config object, stitching together the request and reponses that are passed in
    :param request: a request config object.
    :param responses: a list of response config objects
    :return: a method config object
    """

    return ApiGatewayMethodConfig(method_name=methodname,
                                  lambda_unit=lambda_title,
                                  request_config=request,
                                  response_config=responses,
                                  httpmethod=httpmethod,
                                  authorizationtype=authorizationtype)


def create_api_unit(method_config):
    """
    Creates an API object using a method_config object
    :param method_config: a method config
    :return: an Api gateway object
    """
    return ApiGatewayUnit(apiname, template, [method_config], network_config)


def create_api_leaf(method_config):
    return ApiGatewayLeaf(tree_name, apiname, template, [method_config])


def add_lambda(num):
    """
    Creates a lambda function to use with the api gateway
    :param num: adds a num to the end of resource titles to avoid duplicates.
    :return: a LambdaUnit object
    """

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

    return LambdaUnit(
        unit_title=lambda_title + num,
        template=template,
        dependencies=None,
        stack_config=network_config,
        lambda_config=lambda_config
    )
