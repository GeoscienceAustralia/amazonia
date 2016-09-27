#!/usr/bin/python3
from amazonia.classes.leaf import Leaf
from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject, RemoteReferenceSecurityEnabledObject, \
    LocalReferenceSecurityEnabledObject
from troposphere import Ref, GetAtt, Join, Output
from troposphere.awslambda import Code, VPCConfig, Function, Permission
from troposphere.events import Rule, Target


class Lambda(LocalSecurityEnabledObject):
    def __init__(self, title, template, dependencies, network_config, lambda_config):
        """
        Amazonia lambda unit definition
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html
        https://github.com/cloudtools/troposphere/blob/master/troposphere/awslambda.py
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param template: Troposphere stack to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param network_config: object containing network related variables
        :param lambda_config: object containing lambda related variables
        """
        super(Lambda, self).__init__(vpc=network_config.vpc, title=title, template=template)
        self.title = title
        self.dependencies = dependencies if dependencies else []

        self.function_name = Join('', [Ref('AWS::StackName'),
                                       '-',
                                       lambda_config.lambda_function_name])

        self.trop_lambda_function = template.add_resource(
            Function(self.title,
                     Code=Code(S3Bucket=lambda_config.lambda_s3_bucket, S3Key=lambda_config.lambda_s3_key),
                     Description=lambda_config.lambda_description,
                     FunctionName=self.function_name,
                     Handler=lambda_config.lambda_handler,
                     MemorySize=lambda_config.lambda_memory_size,
                     Role=lambda_config.lambda_role_arn,
                     Runtime=lambda_config.lambda_runtime,
                     Timeout=lambda_config.lambda_timeout,
                     VpcConfig=VPCConfig(SubnetIds=network_config.private_subnets,
                                         SecurityGroupIds=[self.security_group])))

        self.add_egress(receiver=network_config.public_cidr, port='-1')  # All Traffic to Nat gateways

        if lambda_config.lambda_schedule:
            self.cwa_name = Join('', [Ref('AWS::StackName'),
                                      '-',
                                      lambda_config.lambda_function_name + 'Rule'])

            self.trop_cw_rule = template.add_resource(
                Rule(
                    self.title + 'Rule',
                    Name=self.cwa_name,
                    ScheduleExpression=lambda_config.lambda_schedule,
                    State='ENABLED',
                    Targets=[Target(
                        Arn=GetAtt(self.trop_lambda_function, 'Arn'),
                        Id=title
                    )]
                )
            )

            self.trop_cw_permission = template.add_resource(
                Permission(
                    self.title + 'RulePermission',
                    Action='lambda:InvokeFunction',
                    FunctionName=GetAtt(self.trop_lambda_function, 'Arn'),
                    Principal='events.amazonaws.com',
                    SourceArn=GetAtt(self.trop_cw_rule, 'Arn')
                )
            )


class LambdaLeaf(Lambda, Leaf):
    def __init__(self, leaf_title, availability_zones, tree_name, template, dependencies, public_cidr,
                 lambda_config):
        """
        Create a Lambda function within a cross referenced stack
        :param leaf_title: title of the amazonia leaf and associated resources to be used in cloud formation
        :param public_cidr: public cidr pattern, this can either allow public access or restrict to an organisation
        :param availability_zones: List of availability zones autoscaling resources can use
        :param tree_name: name of cross referenced stack
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param lambda_config: object containing lambda related variables
        """
        self.set_tree_config(template=template, availability_zones=availability_zones,
                             tree_name=tree_name)
        self.tree_config.public_cidr = public_cidr
        super(LambdaLeaf, self).__init__(network_config=self.tree_config, title=leaf_title, template=template,
                                         dependencies=dependencies, lambda_config=lambda_config)

        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_leaf_sg = RemoteReferenceSecurityEnabledObject(
                template=template,
                reference_title=self.tree_name + '-' + portless_dependency_name + '-SecurityGroup'
            )
            self.add_flow(receiver=target_leaf_sg, port=dependency_port)

        self.template.add_output(Output(
            'lambdaArn',
            Description='Lambda function ARN',
            Value=GetAtt(self.trop_lambda_function, 'Arn'),
            Export={'Name': self.tree_name + '-' + leaf_title + '-Arn'}
        ))


class LambdaUnit(Lambda):
    def __init__(self, unit_title, template, dependencies, stack_config, lambda_config):
        """
        Create a Lambda function as a unit, part of an integrated stack
        :param unit_title: Title of the Lambda function
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param stack_config: object containing network related variables
        :param lambda_config: object containing lambda related variables
        """
        super(LambdaUnit, self).__init__(network_config=stack_config, title=unit_title, template=template,
                                         dependencies=dependencies, lambda_config=lambda_config)

        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_unit_sg = LocalReferenceSecurityEnabledObject(
                template=template,
                reference_title=portless_dependency_name + 'Sg'
            )
            self.add_flow(receiver=target_unit_sg, port=dependency_port)
