#!/usr/bin/python3
#  pylint: disable=line-too-long

from troposphere import Ref, Tags, Join, Output, GetAtt, ec2, route53, Base64
from amazonia.classes.security_enabled_object import SecurityEnabledObject
from amazonia.classes.sns import SNS


class SingleInstance(SecurityEnabledObject):
    def __init__(self, title, vpc, template, keypair, si_image_id, si_instance_type, subnet, instance_dependencies,
                 alert_emails, alert, iam_instance_profile_arn=None, is_nat=False, hosted_zone_name=None):
        """
        AWS CloudFormation - http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
        Troposphere - https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        Create a singleton instance such as a nat or a jumphost
        :param title: Title of instance e.g 'nat1', 'nat2' or 'jump1'
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param template: The template to add the SingleInstance object to.
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param si_image_id: AWS ami id to create instance from, e.g. 'ami-12345'
        :param si_instance_type: Instance type for single instance e.g. 't2.micro' or 't2.nano'
        :param subnet: Troposhere object for subnet created e.g. 'sub_pub1'
        :param is_nat: a boolean that is used to determine if the instance will be a NAT or not. Default: False
        :param hosted_zone_name: A hosted zone name for setting up a Route 53 record set for Jump hosts
        :param instance_dependencies: a list of dependencies to wait for before creating the single instance.
        :param iam_instance_profile_arn: the ARN for an IAM profile that enables cloudwatch logging.
        :param alert_emails: a list of email addresses to send alerts to if the instance fails the AWS status checks.
        :param alert: a boolean to specify wether or not to alert to alert_emails or not.
        """

        super(SingleInstance, self).__init__(vpc=vpc, title=title, template=template)

        region = subnet.AvailabilityZone[:-1]
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

        self.single = self.template.add_resource(
                           ec2.Instance(
                               title,
                               KeyName=keypair,
                               ImageId=si_image_id,
                               InstanceType=si_instance_type,
                               NetworkInterfaces=[ec2.NetworkInterfaceProperty(
                                   GroupSet=[Ref(self.security_group)],
                                   AssociatePublicIpAddress=True,
                                   DeviceIndex='0',
                                   DeleteOnTermination=True,
                                   SubnetId=Ref(subnet),
                               )],
                               # The below boolean determines whether source/destination checking is enabled on the
                               # instance. This needs to be false to enable NAT functionality from the instance, or
                               # true otherwise. For more info check the below:
                               # http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
                               SourceDestCheck=False if is_nat else True,
                               Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', title])),
                               DependsOn=instance_dependencies,
                               UserData=Base64(userdata)
                               ))

        if is_nat and alert and alert_emails:
            snsname = title + 'topic'
            self.topic = SNS(title, self.template, snsname)

            for email in alert_emails:
                self.topic.add_subscription(email, 'email')

            metric = 'CPUUtilization'
            self.topic.add_alarm(
                description='Alarms when {0} metric {1} reaches {2}'.format(self.single.title, metric, '60'),
                metric=metric,
                namespace='AWS/EC2',
                threshold='60',
                instance=self.single
            )

        if iam_instance_profile_arn:
            self.single.IamInstanceProfile = iam_instance_profile_arn.split('/')[1]

        if self.single.SourceDestCheck == 'true':
            self.si_output(nat=False, subnet=subnet)
        else:
            self.si_output(nat=True, subnet=subnet)

        if hosted_zone_name:

            # Give the instance an Elastic IP Address
            self.eip_address = self.template.add_resource(ec2.EIP(
                self.single.title + 'EIP',
                DependsOn=instance_dependencies,
                Domain='vpc',
                InstanceId=Ref(self.single)
                ))

            # Create a Route53 Record Set for the instances Elastic IP address.

            self.si_r53 = self.template.add_resource(route53.RecordSetType(
                self.single.title + 'R53',
                HostedZoneName=hosted_zone_name,
                Comment='DNS Record for {0}'.format(self.single.title),
                Name=Join('', [Ref('AWS::StackName'), '-', self.single.title, '.', hosted_zone_name]),
                ResourceRecords=[Ref(self.eip_address)],
                Type='A',
                TTL='300',
                DependsOn=instance_dependencies
            ))

            # Create an output for the Record Set that has been created.

            self.template.add_output(Output(
                 self.single.title + 'URL',
                 Description='URL of the jump host {0}'.format(self.single.title),
                 Value=self.si_r53.Name
            ))

    def si_output(self, nat, subnet):
        """
        Function that add the IP output required for single instances depending if it is a NAT or JumpHost
        :param nat: A NAT boolean is defined by the SourceDestCheck=False flag for extracting the ip
        :param subnet: A subnet where the instance lives required for output.
        :return: Troposphere Output object containing IP details
        """

        if nat is True:
            net_interface = 'PrivateIp'
        else:
            net_interface = 'PublicIp'

        self.template.add_output(
             Output(
                 self.single.title,
                 Description='{0} address of {1} single instance'.format(net_interface, self.single.title),
                 Value=Join(' ', ['{0} {1} address'.format(self.single.title, net_interface),
                                  GetAtt(self.single, net_interface),
                                  'on subnet',
                                  Ref(subnet)
                                  ]
                            )
                 ))

    # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
    # TODO Sys Tests: Try connecting to host in another vpc
