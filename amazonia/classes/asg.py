#!/usr/bin/python3

from amazonia.classes.block_devices import Bdm
from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject
from amazonia.classes.util import get_cf_friendly_name
from troposphere import Base64, codedeploy, Ref, Join, Output
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag, NotificationConfigurations
from troposphere.autoscaling import ScalingPolicy, ScheduledAction
from troposphere.cloudwatch import MetricDimension, Alarm
from troposphere.policies import UpdatePolicy, AutoScalingRollingUpdate

class Asg(LocalSecurityEnabledObject):
    def __init__(self, title, template, network_config, load_balancers, asg_config):
        """
        Creates an autoscaling group and codedeploy definition
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param template: Troposphere stack to append resources to
        :param network_config: object containing network related config
        :param asg_config: object containing asg related config
        :param load_balancers: list of load balancers to associate autoscaling group with
        """
        self.title = title + 'Asg'
        super(Asg, self).__init__(vpc=network_config.vpc, title=self.title, template=template)
        self.template = template
        self.network_config = network_config
        self.trop_asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.cw_alarms = []
        self.scaling_polices = []
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

        availability_zones = network_config.availability_zones
        self.trop_asg = self.template.add_resource(AutoScalingGroup(
            title,
            MinSize=asg_config.minsize,
            MaxSize=asg_config.maxsize,
            VPCZoneIdentifier=network_config.private_subnets,
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[Ref(load_balancer) for load_balancer in load_balancers],
            HealthCheckGracePeriod=asg_config.health_check_grace_period,
            HealthCheckType=asg_config.health_check_type,
            Tags=[Tag('Name', Join('', [Ref('AWS::StackName'), '-', title]), True)],
        ))
        if network_config.get_depends_on():
            self.trop_asg.DependsOn = network_config.get_depends_on()

        # Set cloud formation update policy to update
        self.trop_asg.resource['UpdatePolicy'] = UpdatePolicy(
            AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                MinInstancesInService=0
            )
        )

        self.trop_asg.NotificationConfigurations = [
            NotificationConfigurations(TopicARN=network_config.sns_topic,
                                       NotificationTypes=['autoscaling:EC2_INSTANCE_LAUNCH',
                                                          'autoscaling:EC2_INSTANCE_LAUNCH_ERROR',
                                                          'autoscaling:EC2_INSTANCE_TERMINATE',
                                                          'autoscaling:EC2_INSTANCE_TERMINATE_ERROR'])]

        # if there are any scaling policies specified, create and associated with ASG
        if asg_config.simple_scaling_policy_config is not None:
            for scaling_policy_config in asg_config.simple_scaling_policy_config:
                self.create_simple_scaling_policy(scaling_policy_config=scaling_policy_config)

        self.trop_asg.LaunchConfigurationName = Ref(self.create_launch_config(
            title=title,
            asg_config=asg_config,
            network_config=network_config
        ))

        # scale down auto scaling group outside work hours with Scheduled Actions
        if asg_config.ec2_scheduled_shutdown:
            # Recurrence tag uses Cron syntax: https://en.wikipedia.org/wiki/Cron

            # scheduled action for turning off instances (max=0)
            self.template.add_resource(ScheduledAction(
                title=title + 'SchedActOFF',
                AutoScalingGroupName=Ref(self.trop_asg),
                MaxSize=0,
                MinSize=0,
                Recurrence="0 09 * * *"  # 0900 UTC = 2000 AEDT
            ))
            # scheduled action for turning on instances (max=maxsize)
            self.template.add_resource(ScheduledAction(
                title=title + 'SchedActON',
                AutoScalingGroupName=Ref(self.trop_asg),
                MaxSize=asg_config.maxsize,
                MinSize=asg_config.minsize,
                Recurrence="0 19 * * 0,1,2,3,4"  # 1900 UTC (previous day) = 0600 AEDT
            ))

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
            SecurityGroups=[self.security_group],
        ))

        if asg_config.iam_instance_profile_arn is not None:
            self.lc.IamInstanceProfile = asg_config.iam_instance_profile_arn

        # Userdata must be a valid string
        if asg_config.userdata is None:
            self.lc.UserData = ''
        else:
            self.lc.UserData = Base64(asg_config.userdata)

        # If block devices have been configured
        if asg_config.block_devices_config is not None:
            self.lc.BlockDeviceMappings = Bdm(launch_config_title, asg_config.block_devices_config) \
                .block_device_mappings

        return launch_config_title

    def create_simple_scaling_policy(self, scaling_policy_config):
        """
        Simple scaling policy based upon ec2 metrics

        heavy-load
        cpu > 45 for 1 period of 300 seconds add two instances, 45 second cooldown

        light-load
        cpu <= 15 for 6 periods of 300 seconds remove one instance, 120 second cooldown

        medium-load
        cpu >= 25 for 1 period of 300 seconds add one instance, 45 second cooldown

        [name]
        [metric_name] [comparison_operator] [threshold] [evaluation_periods] [period] [scaling_adjustment] [cooldown]

        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-as-policy.html
        :param scaling_policy_config: simple scaling policy config object
        """

        cf_name = self.trop_asg.title + get_cf_friendly_name(scaling_policy_config.name)

        scaling_policy = self.template.add_resource(ScalingPolicy(
            title=cf_name + 'Sp',
            AdjustmentType='ChangeInCapacity',
            AutoScalingGroupName=Ref(self.trop_asg),
            Cooldown=scaling_policy_config.cooldown,
            ScalingAdjustment=scaling_policy_config.scaling_adjustment,
        ))

        self.scaling_polices.append(scaling_policy)

        self.cw_alarms.append(self.template.add_resource(Alarm(
            title=cf_name + 'Cwa',
            AlarmActions=[Ref(scaling_policy), self.network_config.sns_topic],
            AlarmDescription=scaling_policy_config.description,
            AlarmName=cf_name,
            ComparisonOperator=scaling_policy_config.comparison_operator,
            Dimensions=[MetricDimension(
                Name='AutoScalingGroupName',
                Value=Ref(self.trop_asg)
            )],
            EvaluationPeriods=scaling_policy_config.evaluation_periods,
            MetricName=scaling_policy_config.metric_name,
            Namespace='AWS/EC2',
            Period=scaling_policy_config.period,
            Statistic='Average',
            Threshold=scaling_policy_config.threshold,
            OKActions=[self.network_config.sns_topic]
        )))

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
                                       ServiceRoleArn=cd_service_role_arn,
                                       DependsOn=[self.cd_app.title, self.trop_asg.title]))

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
