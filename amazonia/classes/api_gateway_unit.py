#!/usr/bin/python3

from troposphere import Ref, Join, GetAtt, Output
from troposphere.apigateway import RestApi, Resource, MethodResponse, IntegrationResponse, Integration, Method
from troposphere.apigateway import Deployment
from amazonia.classes.lambda_unit import LambdaUnit


class ApiGatewayUnit(object):
    def __init__(self, unit_title, template, method_config, network_config, deployment_config):
        """
        This class creates an API Gateway object with one or multiple methods attached.
        AWS Cloud Formation Links:
        RestApi: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html
        Resource: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-resource.html
        Method: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-method.html
        Integration: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apitgateway-method-integration.html

        Troposhere link:
        https://github.com/cloudtools/troposphere/blob/master/troposphere/apigateway.py

        :param unit_title: The title of the api gateway being created
        :param template: the troposphere template object to update
        :param method_config: a list of one or many ApiGatewayMethodConfig objects with data prefilled from yaml values
        :param network_config: a Network Config object, currently unused but required while this is considered a 'unit'
        :param deployment_config: a list of one or may ApiGatewayDeploymentConfig objects with data prefille from yaml values
        """
        self.title = unit_title
        self.template = template
        self.methods = []
        self.method_responses = []
        self.integration_responses = []
        self.dependencies = []
        self.deployments = []
        self.network_config = network_config
        self.method_config = method_config
        self.deployment_config = deployment_config
        self.endpoints = []

        self.api = self.template.add_resource(RestApi(
                                                      '{0}API'.format(self.title),
                                                      Name=self.title
                                                     )
                                              )

        for method in self.method_config:
            self.dependencies.append(method.lambda_unit)

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
                                  Credentials='',
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
            self.method_responses.append(
                MethodResponse(
                               '{0}Response{1}'.format(method_config.method_name, number),
                               StatusCode=response.statuscode,
                               ResponseModels=response.models,
                               ResponseParameters=response.parameters
                              )
            )

            self.integration_responses.append(
                IntegrationResponse(
                                    '{0}IntegrationResponse{1}'.format(method_config.method_name, number),
                                    StatusCode=response.statuscode,
                                    ResponseParameters=response.parameters,
                                    ResponseTemplates=response.templates,
                                    SelectionPattern=response.selectionpattern
                                   )
            )

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
                             MethodResponses=self.method_responses,
                             RequestParameters=method_config.request.parameters
                             )

        self.method_responses = []
        self.integration_responses = []

        self.methods.append(method)
        self.template.add_resource(method)

    def add_deployment(self, deployment_config):
        """
        Creates a deployment and adds it to this api gateway.
        :param deployment_config: the Deployment Config object with details for the deployment.
        """

        dependencies = []
        for method in self.methods:
            dependencies.append(method.title)

        deployment = Deployment(
                                '{0}{1}Deployment'.format(
                                    self.title, deployment_config.stagename),
                                Description='{0} Deployment created for APIGW {1}'.format(
                                    deployment_config.stagename, self.title),
                                RestApiId=deployment_config.restapiid,
                                StageName=deployment_config.stagename,
                                DependsOn=dependencies
                                )

        self.deployments.append(deployment)
        self.template.add_resource(deployment)

        value = Join('', ['https://',
                          Ref(self.api),
                          '.execute-api.',
                          Ref("AWS::Region"),
                          '.amazonaws.com/',
                          deployment.StageName
                          ]
                     )

        self.endpoints.append(value)

        self.template.add_output(Output(
            deployment.title,
            Description='URL of API deployment: {0}'.format(deployment.title),
            Value=value
        ))

    def add_unit_flow(self, other_unit):
        """
        Creates a method that points at the other_unit object (other_unit should be a lambda_unit)
        :param other_unit: for this class, other unit should always be a lambda unit
        """
        if not isinstance(other_unit, LambdaUnit):
            raise ApiGatewayConfigError('Api Gateway method {0} must be of type LambdaUnit'
                                        .format(other_unit.title))
        lambda_title = other_unit.title

        for method in self.method_config:
            if method.lambda_unit == lambda_title:
                resource = self.create_resource(method)
                self.get_responses(method)
                integration = self.create_integration(method, GetAtt(other_unit.trop_lambda_function, 'Arn'))
                self.add_method(resource, integration, method)

        if self.deployment_config:
            for deployment in self.deployment_config:
                self.add_deployment(deployment)

    def get_dependencies(self):
        """
        :return: list of other unit's this unit is dependant upon
        """
        return self.dependencies

class ApiGatewayConfigError(Exception):
    def __init__(self, value):
        self.value = value
