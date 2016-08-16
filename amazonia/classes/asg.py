#!/usr/bin/python3

from troposphere import Base64, codedeploy, Ref, Join, Output, ec2
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag, NotificationConfigurations

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from amazonia.classes.block_devices import Bdm


class Asg(SecurityEnabledObject):
    def __init__(self, title, template, network_config, load_balancers, asg_config):
        """
        Creates an autoscaling group and codedeploy definition
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param template: Troposphere stack to append resources to
        :param network_config: object containing network related config
        :param asg_config: object containing asg related config
        :param load_balancers: list of load balancers to associate autoscaling group with
        :param block_devices_config: List containing block device mappings
        """
        super(Asg, self).__init__(vpc=network_config.vpc, title=title, template=template)

        self.template = template
        self.title = title + 'Asg'
        self.trop_asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.create_asg(
            title=self.title,
            network_config=network_config,
            load_balancers=load_balancers,
            asg_config=asg_config
        )
        if network_config.cd_service_role_arn is not None:
            self.create_cd_deploygroup(
                title=self.title,
                cd_service_role_arn=network_config.cd_service_role_arn
            )

    def create_asg(self, title, network_config, load_balancers, asg_config):
        """
        Creates an autoscaling group object
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        :param title: Title of the autoscaling application
        :param load_balancers: list of load balancers to associate autoscaling group with
        :param asg_config: object containing asg related variables
        :param network_config: object containing network related variables
        """

        availability_zones = [subnet.AvailabilityZone for subnet in network_config.private_subnets]
        self.trop_asg = self.template.add_resource(AutoScalingGroup(
            title,
            MinSize=asg_config.minsize,
            MaxSize=asg_config.maxsize,
            VPCZoneIdentifier=[Ref(subnet.title) for subnet in network_config.private_subnets],
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[Ref(load_balancer) for load_balancer in load_balancers],
            HealthCheckGracePeriod=asg_config.health_check_grace_period,
            HealthCheckType=asg_config.health_check_type,
            Tags=[Tag('Name', Join('', [Ref('AWS::StackName'), '-', title]), True)])
        )

        if asg_config.sns_topic_arn is not None:
            if asg_config.sns_notification_types is not None and isinstance(asg_config.sns_notification_types, list):
                self.trop_asg.NotificationConfigurations = [
                    NotificationConfigurations(TopicARN=asg_config.sns_topic_arn,
                                               NotificationTypes=asg_config.sns_notification_types)]
            else:
                raise MalformedSNSError('Error: sns_notification_types must be a non null list.')

        self.trop_asg.LaunchConfigurationName = Ref(self.create_launch_config(
            title=title,
            asg_config=asg_config,
            network_config=network_config
        ))
        if asg_config.userdata is None:
            self.lc.UserData = ''

    def create_launch_config(self, title, asg_config, network_config):
        """
        Method to add a launch configuration resource to a cloud formation document
        AWS Cloud Formation links:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig.html
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-launchconfig-blockdev-mapping.html
        Troposphere links:
        https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param title: Title of the autoscaling application
        :param asg_config: object holding asg related variables
        :param network_config: object holding network related variables
        :return string representing Launch Configuration name
        """
        launch_config_title = title + 'Lc'

        self.lc = self.template.add_resource(LaunchConfiguration(
            launch_config_title,
            AssociatePublicIpAddress=False,
            ImageId=asg_config.image_id,
            InstanceMonitoring=False,
            InstanceType=asg_config.instance_type,
            KeyName=network_config.keypair,
            SecurityGroups=[Ref(self.security_group.name)],
        ))
        if asg_config.iam_instance_profile_arn is not None:
            self.lc.IamInstanceProfile = asg_config.iam_instance_profile_arn
        self.lc.UserData = Base64(asg_config.userdata)

        self.lc.BlockDeviceMappings = Bdm(launch_config_title, asg_config.block_devices_config).bdm
        return launch_config_title

    def create_cd_deploygroup(self, title, cd_service_role_arn):
        """
        Creates a CodeDeploy application and deploy group and associates with autoscaling group
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codedeploy-deploymentgroup.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/codedeploy.py
        :param title: Title of the code deploy application
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        :return 2 strings representing CodeDeploy Application name and CodeDeploy Group name.
        """
        cd_app_title = title + 'Cda'
        cd_deploygroup_title = title + 'Cdg'

        self.cd_app = self.template.add_resource(codedeploy.Application(cd_app_title,
                                                                        ApplicationName=Join('', [Ref('AWS::StackName'),
                                                                                                  '-', cd_app_title])))
        self.cd_deploygroup = self.template.add_resource(
            codedeploy.DeploymentGroup(cd_deploygroup_title,
                                       ApplicationName=Ref(self.cd_app),
                                       AutoScalingGroups=[Ref(self.trop_asg)],
                                       DeploymentConfigName='CodeDeployDefault.OneAtATime',
                                       DeploymentGroupName=Join('', [Ref('AWS::StackName'),
                                                                     '-', cd_deploygroup_title]),
                                       ServiceRoleArn=cd_service_role_arn))
        self.cd_deploygroup.DependsOn = [self.cd_app.title, self.trop_asg.title]

        # Outputs
        self.template.add_output(
            Output(
                self.cd_deploygroup.title,
                Description='Code Deploy Deployment Group',
                Value=self.cd_deploygroup.DeploymentGroupName
            ))

        self.template.add_output(
            Output(
                self.cd_app.title,
                Description='Code Deploy Application',
                Value=Join('', ['https://',
                                Ref('AWS::Region'),
                                '.console.aws.amazon.com/codedeploy/home?region=',
                                Ref('AWS::Region'),
                                '#/applications/',
                                self.cd_app.ApplicationName])
            ))

        return cd_app_title, cd_deploygroup_title


class MalformedSNSError(Exception):
    def __init__(self, value):
        self.value = value
