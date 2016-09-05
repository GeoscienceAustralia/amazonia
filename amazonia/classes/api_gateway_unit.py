#!/usr/bin/python3

from troposphere import Ref, Join, GetAtt
from troposphere.apigateway import RestApi, Resource, MethodResponse, IntegrationResponse, Integration, Method


class ApiGatewayUnit(object):
    def __init__(self, unit_title, template, method_config, network_config):
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
        """
        self.title = unit_title
        self.template = template
        self.methods = []
        self.method_responses = []
        self.integration_responses = []
        self.dependencies = []
        self.network_config = network_config

        self.api = self.template.add_resource(RestApi(
                                                      '{0}API'.format(self.title),
                                                      Name=self.title
                                                     )
                                             )

        for method in method_config:

            resource = self.create_resource(method)
            self.get_responses(method)

            integration = self.create_integration(method)

            method = Method(
                            '{0}Method'.format(method.method_name),
                            RestApiId=Ref(self.api),
                            AuthorizationType=method.authorizationtype,
                            ResourceId=Ref(resource),
                            HttpMethod=method.httpmethod,
                            Integration=integration,
                            MethodResponses=self.method_responses,
                            RequestParameters=method.request.parameters
                            )
            self.methods.append(method)
            self.template.add_resource(method)

    def create_resource(self, method_config):
        """
        Creates a resource using a single provided ApiGatewayMethodConfig object.
        :param method_config: a single ApiGatewayMethodConfig object
        :return: a troposphere Resource object that links the API with methods
        """

        return self.template.add_resource(Resource(
                                                   '{0}{1}'.format(self.api.title, method_config.method_name),
                                                   ParentId=GetAtt(self.api.title, 'RootResourceId'),
                                                   RestApiId=Ref(self.api),
                                                   PathPart=method_config.method_name
                                                   )
                                         )

    def create_integration(self, method_config):
        """
        Creates an integration object using a single provided ApiGatewayMethodConfig object.
        :param method_config: a single ApiGatewayMethodConfig object
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
                                                method_config.lambda_arn,
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

    def get_dependencies(self):
        """
        :return: returns an empty list as an ApiGatewayUnit has no upstream dependencies
        """
        return self.dependencies
