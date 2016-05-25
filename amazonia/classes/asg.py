#!/usr/bin/python3

from troposphere import Base64, codedeploy, Ref, Join, Output
from troposphere.autoscaling import AutoScalingGroup, LaunchConfiguration, Tag, NotificationConfigurations

from amazonia.classes.security_enabled_object import SecurityEnabledObject


class Asg(SecurityEnabledObject):
    def __init__(self, title, vpc, template, minsize, maxsize, subnets, load_balancer,
                 keypair, image_id, instance_type, health_check_grace_period, health_check_type,
                 iam_instance_profile_arn, userdata, sns_topic_arn, sns_notification_types, cd_service_role_arn):
        """
        Creates an autoscaling group and codedeploy definition
        :param title: Title of the autoscaling application e.g 'webApp1', 'api2' or 'dataprocessing'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param template: Troposphere stack to append resources to
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param subnets: subnets to create autoscaled instances in
        :param load_balancer: load balancer to associate autoscaling group with
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param health_check_grace_period: Time given to an instance before asg attempts to test it
        :param health_check_type: either test health according to ELB or EC2 instance status check
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param userdata: Instance boot script
        :param sns_topic_arn: ARN for sns topic to notify regarding autoscale events
        :param sns_notification_types: list of SNS autoscale notification types
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        """
        super(Asg, self).__init__(vpc=vpc, title=title, template=template)
        if maxsize < minsize:
            raise MinMaxError("Error: minsize must be lower than maxsize.")

        self.template = template
        self.title = title + 'Asg'
        self.trop_asg = None
        self.lc = None
        self.cd_app = None
        self.cd_deploygroup = None
        self.sns_notification_configurations = None
        self.create_asg(
            title=self.title,
            minsize=minsize,
            maxsize=maxsize,
            subnets=subnets,
            load_balancer=load_balancer,
            keypair=keypair,
            image_id=image_id,
            instance_type=instance_type,
            health_check_grace_period=health_check_grace_period,
            health_check_type=health_check_type,
            iam_instance_profile_arn=iam_instance_profile_arn,
            sns_topic_arn=sns_topic_arn,
            sns_notification_types=sns_notification_types,
            userdata=userdata
        )
        if cd_service_role_arn is not None:
            self.create_cd_deploygroup(
                title=self.title,
                cd_service_role_arn=cd_service_role_arn
            )

    def create_asg(self, title, minsize, maxsize, subnets, load_balancer, keypair, image_id, instance_type,
                   health_check_grace_period, health_check_type, iam_instance_profile_arn, userdata, sns_topic_arn,
                   sns_notification_types):
        """
        Creates an autoscaling group object
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        :param title: Title of the autoscaling application
        :param minsize: minimum size of autoscaling group
        :param maxsize: maximum size of autoscaling group
        :param subnets: subnets to create autoscaled instances in
        :param load_balancer: load balancer to associate autoscaling group with
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param health_check_grace_period: Time given to an instance before asg attempts to test it
        :param health_check_type: either test health according to ELB or EC2 instance status check
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param userdata: Instance boot script
        :param sns_topic_arn: ARN for sns topic to notify regarding autoscale events
        :param sns_notification_types: list of SNS autoscale notification types
        :return string representing Auto Scaling Group name
        """

        availability_zones = [subnet.AvailabilityZone for subnet in subnets]
        self.trop_asg = self.template.add_resource(AutoScalingGroup(
            title,
            MinSize=minsize,
            MaxSize=maxsize,
            VPCZoneIdentifier=[Ref(subnet.title) for subnet in subnets],
            AvailabilityZones=availability_zones,
            LoadBalancerNames=[Ref(load_balancer)],
            HealthCheckGracePeriod=health_check_grace_period,
            HealthCheckType=health_check_type,
            Tags=[Tag('Name', Join('', [Ref('AWS::StackName'), '-', title]), True)])
        )

        if sns_topic_arn is not None:
            if sns_notification_types is not None and isinstance(sns_notification_types, list):
                self.sns_notification_configurations = self.trop_asg.NotificationConfigurations = \
                    [NotificationConfigurations(TopicARN=sns_topic_arn, NotificationTypes=sns_notification_types)]
            else:
                raise MalformedSNSError("Error: sns_notification_types must be a non null list.")

        self.trop_asg.LaunchConfigurationName = Ref(self.create_launch_config(
            title=title,
            keypair=keypair,
            image_id=image_id,
            instance_type=instance_type,
            iam_instance_profile_arn=iam_instance_profile_arn,
            userdata=userdata if userdata is not None else ""
        ))
        return title

    def create_launch_config(self, title, keypair, image_id, instance_type, iam_instance_profile_arn, userdata):
        """
        Method to add a launch configuration resource to a cloud formation document
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/autoscaling.py
        :param title: Title of the autoscaling application
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param image_id: AWS ami id to create instances from, e.g. 'ami-12345'
        :param instance_type: Instance type to create instances of e.g. 't2.micro' or 't2.nano'
        :param iam_instance_profile_arn: Iam instance profile ARN to allow isntance access to services like S3
        :param userdata: Instance boot script
        :return string representing Launch Configuration name
        """
        launch_config_title = title + 'Lc'

        self.lc = self.template.add_resource(LaunchConfiguration(
            launch_config_title,
            AssociatePublicIpAddress=False,
            ImageId=image_id,
            InstanceMonitoring=False,
            InstanceType=instance_type,
            KeyName=keypair,
            SecurityGroups=[Ref(self.security_group.name)],
        ))
        if iam_instance_profile_arn is not None:
            self.lc.IamInstanceProfile = iam_instance_profile_arn
        self.lc.UserData = Base64(userdata)
        return launch_config_title

    def create_cd_deploygroup(self, title, cd_service_role_arn):
        """
        Creates a CodeDeploy application and deploy group and associates with autoscaling group
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
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

        """ Outputs
        """
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


class MinMaxError(Exception):
    def __init__(self, value):
        self.value = value


class MalformedSNSError(Exception):
    def __init__(self, value):
        self.value = value
