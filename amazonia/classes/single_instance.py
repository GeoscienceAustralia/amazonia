#!/usr/bin/python3
#  pylint: disable=line-too-long

from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject
from troposphere import Ref, Tags, Join, Output, ec2, route53, Base64


class SingleInstance(LocalSecurityEnabledObject):
    def __init__(self, title, template, single_instance_config):
        """
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        Create a singleton instance such as a nat or a jumphost
        :param title: Title of instance e.g 'nat1', 'nat2' or 'jump1'
        :param template: The template to add the SingleInstance object to.
        :param single_instance_config: object containing variables specific to single instance configuration
        """

        super(SingleInstance, self).__init__(vpc=single_instance_config.vpc, title=title, template=template)
        self.sns_topic = single_instance_config.sns_topic
        region = single_instance_config.availability_zone[:-1]
        userdata = """#cloud-config
# Capture all cloud-config output into a more readable logfile
output: {all: '| tee -a /var/log/cloud-init-output.log'}
# update and install packages, reboot if necessary
package_upgrade: true
package_reboot_if_required: true
packages:
 - perl-Switch
 - perl-DateTime
 - perl-Sys-Syslog
 - perl-LWP-Protocol-https

write_files:
 - path: /etc/awslogs.cfg
   content: |
    [general]
    state_file = /var/awslogs/state/agent-state

    [/var/log/messages]
    file = /var/log/messages
    log_group_name = /var/log/messages
    log_stream_name = {instance_id}
    datetime_format = %b %d %H:%M:%S

runcmd:
# cloudwatch monitoring scripts
 - curl -so /tmp/CloudWatchMonitoringScripts-1.2.1.zip http://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.1.zip
 - unzip -d /opt /tmp/CloudWatchMonitoringScripts-1.2.1.zip
 - echo '*/5 * * * * root /opt/aws-scripts-mon/mon-put-instance-data.pl --mem-util --mem-used --mem-avail --disk-space-util --disk-path=/ --from-cron' > /etc/cron.d/cloudwatch
# cloudwatch logs agent and forwarding config
 - curl https://s3.amazonaws.com/aws-cloudwatch/downloads/latest/awslogs-agent-setup.py -O
 - chmod +x ./awslogs-agent-setup.py
 - ./awslogs-agent-setup.py -n -r """ + region + """ -c /etc/awslogs.cfg
"""

        tags = Tags(Name=Join('', [Ref('AWS::StackName'), '-', title]))
        if single_instance_config.ec2_scheduled_shutdown:
            # 2000 UTC (previous day) = 0700 AEDT, 0800 UTC = 1900 AEDT
            # therefore, it needs to run Sunday UTC to be Monday AEDT
            #
            # <start time>;<stop time>;utc;<active days>
            tags += Tags(**{'scheduler:ec2-startstop': '1900;0900;utc;sun,mon,tue,wed,thu'})

        self.single = self.template.add_resource(
            ec2.Instance(
                title,
                KeyName=single_instance_config.keypair,
                ImageId=single_instance_config.si_image_id,
                InstanceType=single_instance_config.si_instance_type,
                NetworkInterfaces=[ec2.NetworkInterfaceProperty(
                    GroupSet=[self.security_group],
                    AssociatePublicIpAddress=True,
                    DeviceIndex='0',
                    DeleteOnTermination=True,
                    SubnetId=single_instance_config.subnet,
                )],
                # The below boolean determines whether source/destination checking is enabled on the
                # instance. This needs to be false to enable NAT functionality from the instance, or
                # true otherwise. For more info check the below:
                # http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
                SourceDestCheck=False if single_instance_config.is_nat else True,
                Tags=tags,
                DependsOn=single_instance_config.instance_dependencies,
                UserData=Base64(userdata)
            ))

        if single_instance_config.is_nat:
            metric = 'CPUUtilization'
            self.sns_topic.add_alarm(
                description='Alarms when {0} metric {1} reaches {2}'.format(self.single.title, metric, '60'),
                metric=metric,
                namespace='AWS/EC2',
                threshold='60',
                instance=self.single
            )

        if single_instance_config.iam_instance_profile_arn:
            self.single.IamInstanceProfile = single_instance_config.iam_instance_profile_arn.split('/')[1]

        if self.single.SourceDestCheck == 'true':
            # Give the instance an Elastic IP Address
            self.eip_address = self.template.add_resource(ec2.EIP(
                self.single.title + 'EIP',
                DependsOn=single_instance_config.instance_dependencies,
                Domain='vpc',
                InstanceId=Ref(self.single)
            ))
            if single_instance_config.public_hosted_zone_name:
                # Create a Route53 Record Set for the instances Elastic IP address.

                self.si_r53 = self.template.add_resource(route53.RecordSetType(
                    self.single.title + 'R53',
                    HostedZoneName=single_instance_config.public_hosted_zone_name,
                    Comment='DNS Record for {0}'.format(self.single.title),
                    Name=Join('', [Ref('AWS::StackName'), '-', self.single.title, '.',
                                   single_instance_config.public_hosted_zone_name]),
                    ResourceRecords=[Ref(self.eip_address)],
                    Type='A',
                    TTL='300',
                    DependsOn=single_instance_config.instance_dependencies
                ))

                # Create an output for the Record Set that has been created.

                self.template.add_output(Output(
                    self.single.title,
                    Description='URL of the jump host {0}'.format(self.single.title),
                    Value=self.si_r53.Name
                ))

            else:
                self.template.add_output(Output(
                    self.single.title,
                    Description='Public IP of the jump host {0}'.format(self.single.title),
                    Value=Ref(self.eip_address)
                ))
