#!/usr/bin/python3

from troposphere import Ref, Tags, Join, Output, GetAtt, ec2
from amazonia.classes.security_enabled_object import SecurityEnabledObject


class SingleInstance(SecurityEnabledObject):
    def __init__(self, title, vpc, template, keypair, si_image_id, si_instance_type, subnet, is_nat=False):
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
        """

        super(SingleInstance, self).__init__(vpc=vpc, title=title, template=template)

        self.single = self.template.add_resource(
                           ec2.Instance(
                               title,
                               KeyName=keypair,
                               ImageId=si_image_id,
                               InstanceType=si_instance_type,
                               NetworkInterfaces=[ec2.NetworkInterfaceProperty(
                                   GroupSet=[Ref(self.security_group)],
                                   AssociatePublicIpAddress=True,
                                   DeviceIndex="0",
                                   DeleteOnTermination=True,
                                   SubnetId=Ref(subnet),
                               )],
                               # The below boolean determines whether source/destination checking is enabled on the
                               # instance. This needs to be false to enable NAT functionality from the instance, or
                               # true otherwise. For more info check the below:
                               # http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html#cfn-ec2-instance-sourcedestcheck
                               SourceDestCheck=False if is_nat else True,
                               Tags=Tags(Name=Join("", [Ref('AWS::StackName'), '-', title]))
                           ))

        if self.single.SourceDestCheck == 'true':
            self.si_output(nat=False, subnet=subnet)
        else:
            self.si_output(nat=True, subnet=subnet)

    def si_output(self, nat, subnet):
        """
        Function that add the IP output required for single instances depending if it is a NAT or JumpHost
        :param nat: A NAT boolean is defined by the SourceDestCheck=False flag for extracting the ip
        :param subnet: A subnet where the instance lives required for output.
        :return: Troposphere Output object containing IP details
        """

        if nat is True:
            net_interface = "PrivateIp"
        else:
            net_interface = "PublicIp"

        self.template.add_output(
             Output(
                 self.single.title,
                 Description='{0} address of {1} single instance'.format(net_interface, self.single.title),
                 Value=Join(" ", ["{0} {1} address".format(self.single.title, net_interface),
                                  GetAtt(self.single, net_interface),
                                  "on subnet",
                                  Ref(subnet)
                                  ]
                            )
                 ))

    # TODO Sys Tests: Connect from jumphost to subpub1 instance, subpub2 instance, can't connect on port 80,8080,443
    # TODO Sys Tests: Try connecting to host in another vpc
