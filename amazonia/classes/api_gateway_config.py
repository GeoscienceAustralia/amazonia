#!/usr/bin/python3


class ApiGatewayMethodConfig(object):
    def __init__(self, method_name, lambda_arn, request_config, response_config, httpmethod, authorizationtype):
        """
        Simple config class for block device mappings for multiple disks
        AWS Cloud Formation Links:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigateway-restapi.html

        Troposhere link:
        https://github.com/cloudtools/troposphere/blob/master/troposphere/apigateway.py
        """

        self.method_name = method_name
        self.lambda_arn = lambda_arn
        self.request = request_config
        self.responses = response_config
        self.httpmethod = httpmethod
        self.authorizationtype = authorizationtype


class ApiGatewayRequestConfig(object):
    def __init__(self, templates, parameters):
        """

        """
        self.templates = templates
        self.parameters = parameters


class ApiGatewayResponseConfig(ApiGatewayRequestConfig):
    def __init__(self, templates, parameters, statuscode, models, selectionpattern):
        """

        """

        super(ApiGatewayResponseConfig, self).__init__(templates, parameters)

        self.statuscode = statuscode
        self.models = models
        self.selectionpattern = selectionpattern
