#!/usr/bin/python3

from troposphere import Ref, Join, GetAtt
from troposphere.apigateway import RestApi, Resource, MethodResponse, IntegrationResponse, Integration, Method


class ApiGateway(object):
    def __init__(self, title, template, method_configs):
        """
        """
        self.title = title
        self.template = template
        self.methods = []
        self.method_responses = []
        self.integration_responses = []

        self.api = self.template.add_resource(RestApi(
                                                      '{0}API'.format(title),
                                                      Name=title
                                                     )
                                             )

        for method_config in method_configs:
            resource = self.template.add_resource(Resource(
                                                           '{0}{1}'.format(self.api.title, method_config.method_name),
                                                           ParentId=GetAtt(self.api.title, 'RootResourceId'),
                                                           RestApiId=Ref(self.api),
                                                           PathPart=method_config.method_name
                                                           )
                                                 )

            self.get_responses(method_config)

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

            integration.resource['PassthroughBehavior'] = "WHEN_NO_TEMPLATES"

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
            self.methods.append(method)
            self.template.add_resource(method)

    def get_responses(self, method_config):
        """

        :param method_config:
        :return:
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
                                    ResponseTemplates=response.templates
                                   )
            )
