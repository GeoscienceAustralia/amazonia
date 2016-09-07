from amazonia.classes.api_gateway_config import ApiGatewayMethodConfig, ApiGatewayDeploymentConfig
from amazonia.classes.api_gateway_config import ApiGatewayResponseConfig, ApiGatewayRequestConfig
from amazonia.classes.api_gateway_unit import ApiGatewayUnit
from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.lambda_unit import LambdaUnit
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from nose.tools import *
from troposphere import Template, ec2, Ref, Join, Tags

template = apiname = methodname = httpmethod = authorizationtype = request_template = request_parameters = \
    response_template = response_parameters = response_models = selection_pattern = statuscode = lambda_title = None


def setup_resources():
    """
    Initialise resources before each test
    """
    global template, apiname, methodname, httpmethod, authorizationtype, request_template, lambda_title, \
        request_parameters, response_template, response_parameters, response_models, selection_pattern, statuscode

    template = None
    template = Template()
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
    assert_equals(response.selectionpattern, selection_pattern)
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
    assert_equals(method.lambda_unit, lambda_title)
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
    global apiname, methodname, lambda_title
    apiname = 'test1'
    methodname = 'login1'
    lambda_title += '1'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)
    lambda_unit = add_lambda('1')
    api.add_unit_flow(lambda_unit)

    print(lambda_title)

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
    global apiname, methodname, lambda_title
    apiname = 'test2'
    methodname = 'login2'
    lambda_title += '2'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)
    lambda_unit = add_lambda('2')
    api.add_unit_flow(lambda_unit)
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


@with_setup(setup_resources())
def test_creation_of_deployment():
    """
    Tests the creation of a demployment
    """
    global apiname, methodname, lambda_title

    apiname = 'test3'
    methodname = 'login3'
    request = create_request_config()
    response = create_response_config()
    method = create_method_config(request, [response])
    api = create_api(method)
    deployment = ApiGatewayDeploymentConfig(
        apiname=api.api.title,
        stagename='Test'
    )
    api.add_deployment(deployment)

    assert_equals(api.deployments[0].title, '{0}{1}Deployment'.format(apiname, deployment.stagename))
    assert_equals(api.deployments[0].Description, '{0} Deployment created for APIGW {1}'.format(deployment.stagename,
                                                                                                apiname))
    assert_equals(type(api.deployments[0].RestApiId), Ref)
    assert_equals(api.deployments[0].StageName, deployment.stagename)


@with_setup(setup_resources())
def create_request_config():
    """
    Create a request config
    :return: a request config object
    """

    return ApiGatewayRequestConfig(templates=request_template,
                                   parameters=request_parameters)


@with_setup(setup_resources())
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


@with_setup(setup_resources())
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


@with_setup(setup_resources())
def create_api(method_config):
    """
    Creates an API object using a method_config object
    :param method_config: a method config
    :return: an Api gateway object
    """

    return ApiGatewayUnit(apiname, template, [method_config], None, None)


@with_setup(setup_resources())
def add_lambda(num):
    """
    Creates a lambda function to use with the api gateway
    :param num: adds a num to the end of resource titles to avoid duplicates.
    :return: a LambdaUnit object
    """

    vpc = template.add_resource(ec2.VPC('myVpc' + num,
                                        CidrBlock='10.0.0.0/16'))
    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway' + num,
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment' + num,
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc),
                                                   DependsOn=internet_gateway.title))
    private_subnets = [template.add_resource(ec2.Subnet('MyPrivSub1' + num,
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub2' + num,
                                                        AvailabilityZone='ap-southeast-2b',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.2.0/24')),
                       template.add_resource(ec2.Subnet('MyPrivSub3' + num,
                                                        AvailabilityZone='ap-southeast-2c',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.3.0/24'))]
    public_subnets = [ec2.Subnet('MySubnet2' + num,
                                 AvailabilityZone='ap-southeast-2a',
                                 VpcId=Ref(vpc),
                                 CidrBlock='10.0.2.0/24')]
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=vpc.title,
        alert=False,
        alert_emails=['some@email.com'],
        public_hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )
    nat = SingleInstance(title='Nat' + num,
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
        lambda_timeout=1,
        lambda_schedule='cron(0/5 * * * ? *)'
    )

    return LambdaUnit(
        unit_title=lambda_title,
        template=template,
        dependencies=None,
        network_config=network_config,
        lambda_config=lambda_config
    )
