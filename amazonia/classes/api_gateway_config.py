#!/usr/bin/python3


class ApiGatewayMethodConfig(object):
    def __init__(self, method_name, lambda_unit, request_config, response_config, httpmethod, authorizationtype):
        """
        This class is used to hold the configuration required for an API Gateway Method
        """

        self.method_name = method_name
        self.lambda_unit = lambda_unit
        self.request = request_config
        self.responses = response_config
        self.httpmethod = httpmethod
        self.authorizationtype = authorizationtype


class ApiGatewayRequestConfig(object):
    def __init__(self, templates, parameters):
        """
        This class is used to hold the configuration required for an Api Gateway Request.
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
