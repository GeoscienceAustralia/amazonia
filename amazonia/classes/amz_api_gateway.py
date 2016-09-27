#!/usr/bin/python3

from troposphere import Ref, Join, GetAtt, Output, ImportValue
from troposphere.apigateway import Deployment
from troposphere.apigateway import RestApi, Resource, MethodResponse, IntegrationResponse, Integration, Method
from troposphere.awslambda import Permission


class ApiGateway(object):
    def __init__(self, title, template, method_config):
        """
        This class creates an API Gateway object with one or multiple methods attached.
        AWS Cloud Formation Links:
        RestApi: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
        Resource: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html
        Method: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html
        Integration:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html
        Troposhere link:
        https://github.com/cloudtools/troposphere/blob/master/troposphere/apigateway.py
        :param title: title of the api gateway and associated resources to be used in cloud formation
        :param template: the troposphere template object to update
        :param method_config: a list of one or many ApiGatewayMethodConfig objects with data prefilled from yaml values
        values
        """
        self.title = title
        self.template = template
        self.methods = []
        self.method_responses = []
        self.integration_responses = []
        self.method_config = method_config
        self.permissions = []

        self.api = self.template.add_resource(
            RestApi(self.title, Name=Join('-', [Ref('AWS::StackName'), title]))
        )

        for method in self.method_config:
            resource = self.create_resource(method)
            self.get_responses(method)
            integration = self.create_integration(
                method,
                self.get_lambda_reference(method.lambda_unit)
            )
            self.add_method(resource, integration, method)

        dependencies = []
        for method in self.methods:
            dependencies.append(method.title)

        self.deployment = Deployment(
            '{0}Deployment'.format(
                self.title),
            Description=Join('', [Ref('AWS::StackName'), ' Deployment created for APIGW ', self.title]),
            RestApiId=Ref(self.api),
            StageName='amz_deploy',
            DependsOn=dependencies
        )

        self.template.add_resource(self.deployment)

        self.template.add_output(Output(
            self.deployment.title + 'URL',
            Description='URL of API deployment: {0}'.format(self.deployment.title),
            Value=Join('', ['https://',
                            Ref(self.api),
                            '.execute-api.',
                            Ref("AWS::Region"),
                            '.amazonaws.com/',
                            self.deployment.StageName
                            ]
                       )
        ))

    def create_resource(self, method_config):
        """
        Creates a resource using a single provided ApiGatewayMethodConfig object.
        :param method_config: a single ApiGatewayMethodConfig object
        :return: a troposphere Resource object that links the API with the method_config provided
        """

        return self.template.add_resource(Resource(
            '{0}{1}'.format(self.api.title, method_config.method_name),
            ParentId=GetAtt(self.api.title, 'RootResourceId'),
            RestApiId=Ref(self.api),
            PathPart=method_config.method_name
        )
        )

    def create_integration(self, method_config, lambda_arn):
        """
        Creates an integration object using a single provided ApiGatewayMethodConfig object.
        :param method_config: a single ApiGatewayMethodConfig object
        :param lambda_arn: the ARN of a lambda function to point this integration at.
        :return: a troposphere integration object
        """

        integration = Integration(
            '{0}Integration'.format(method_config.method_name),
            Type='AWS',
            IntegrationHttpMethod=method_config.httpmethod,
            IntegrationResponses=self.integration_responses,
            RequestTemplates=method_config.request.templates,
            Uri=Join('',
                     [
                         'arn:aws:apigateway:ap-southeast-2:lambda:path/2015-03-31/functions/',
                         lambda_arn,
                         '/invocations'
                     ]
                     )
        )

        perm = self.template.add_resource(Permission(
            '{0}Permission'.format(integration.title),
            Action='lambda:InvokeFunction',
            FunctionName=lambda_arn,
            Principal='apigateway.amazonaws.com'
        ))

        self.permissions.append(perm)
        # At time of creation of this class, the PassthroughBehavior parameter is not implemented for integrations
        # in troposphere. The below assigns it for now. This can be reworked into the above troposphere object once
        # troposphere is updated.
        integration.resource['PassthroughBehavior'] = "WHEN_NO_TEMPLATES"

        return integration

    def get_responses(self, method_config):
        """
        Creates a method and integration response object in troposphere from a provided ApiGatewayMethodConfig object.
        :param method_config: a preconfigured ApiGatewayMethodConfig object
        """

        self.method_responses = []
        self.integration_responses = []

        for number, response in enumerate(method_config.responses):
            method_response = MethodResponse(
                '{0}Response{1}'.format(method_config.method_name, number),
                StatusCode=response.statuscode
            )

            if response.models:
                method_response.ResponseModels = response.models

            integration_response = IntegrationResponse(
                '{0}IntegrationResponse{1}'.format(method_config.method_name, number),
                StatusCode=response.statuscode,
                ResponseTemplates=response.templates,
                SelectionPattern=response.selectionpattern
            )

            if response.parameters:
                method_response.ResponseParameters = response.parameters
                integration_response.ResponseParameters = response.parameters

            self.integration_responses.append(integration_response)
            self.method_responses.append(method_response)

    def add_method(self, resource, integration, method_config):
        """
        Creates a Method as a part of this api and adds it to the template.
        :param resource: The resource that has been created for this api/method pair.
        :param integration: An Integration object for this method.
        :param method_config: The method_config object with details for the method.
        """

        method = Method(
            '{0}Method'.format(method_config.method_name),
            RestApiId=Ref(self.api),
            AuthorizationType=method_config.authorizationtype,
            ResourceId=Ref(resource),
            HttpMethod=method_config.httpmethod,
            Integration=integration,
            MethodResponses=self.method_responses
        )

        if method_config.request.parameters:
            method.RequestParameters = method_config.request.parameters

        self.method_responses = []
        self.integration_responses = []

        self.methods.append(method)
        self.template.add_resource(method)

    def get_lambda_reference(self, lambda_name):
        """
        Define abstract method to be overridden by implementing classes
        :param lambda_name: amazonia name of lamda
        """
        raise NotImplementedError("Please Implement this method")


class ApiGatewayLeaf(ApiGateway):
    def __init__(self, tree_name, leaf_title, template, method_config):
        """
        Create an APi Gateway as a leaf, part of cross referenced stack
        :param leaf_title: title of the API Gateway as part of cross referenced stack
        :param tree_name: name of cross referenced stack
        :param template: troposphere template
        :param method_config: a list of one or many ApiGatewayMethodConfig objects with data prefilled from yaml values
        values
        """
        self.tree_name = tree_name
        super(ApiGatewayLeaf, self).__init__(leaf_title, template, method_config)
        self.template.add_output(Output(
            self.deployment.title + 'Endpoint',
            Description='Endpoint of API deployment: {0}'.format(self.deployment.title),
            Value=Join('', [
                Ref(self.api),
                '.execute-api.',
                Ref("AWS::Region"),
                '.amazonaws.com']
                       ),
            Export={'Name': self.tree_name + '-' + self.title + '-Endpoint'}
        ))

    def get_lambda_reference(self, lambda_name):
        """
        Return the lambda arn from a different stack in the same tree
        :param lambda_name: amazonia name of lamda
        :return: The ARN of the target Lambda
        """
        return ImportValue(self.tree_name + '-' + lambda_name + '-Arn')


class ApiGatewayUnit(ApiGateway):
    def __init__(self, unit_title, template, method_config, stack_config):
        """
        Create an APi Gateway as a unit, part of an integrated stack
        :param unit_title: title of the API Gateway as part of an integrated stack
        :param template: troposphere template
        :param stack_config: shared stack configuration object to store generated API Gateway endpoint
        :param method_config: a list of one or many ApiGatewayMethodConfig objects with data prefilled from yaml values
        values
        """
        super(ApiGatewayUnit, self).__init__(title=unit_title, template=template,
                                             method_config=method_config)
        self.stack_config = stack_config

        self.stack_config.endpoints[unit_title] = Join('', [
            Ref(self.api),
            '.execute-api.',
            Ref("AWS::Region"),
            '.amazonaws.com']
                                                       )

    def get_lambda_reference(self, lambda_name):
        """
        Return the lambda arn from a lambda unit
        :param lambda_name: amazonia name of lamda
        :return: The ARN of the target Lambda
        """
        return GetAtt(lambda_name, 'Arn')
