#!/usr/bin/python3

from amazonia.classes.util import get_cf_friendly_name
from troposphere import ec2, ImportValue, Ref, Tags, Join


class SecurityEnabledObject(object):
    def __init__(self, template, title):
        """
        A Class to enable uni-directional flow when given two security groups
        :param template: The troposphere template object that will be updated with this object
        :param title: the Title of the object eg: unit01ELB, unit01ASG
        :return: a security group, and the ability to create ingress and egress rules
        """

        self.template = template
        self.title = title
        self.security_group = None
        self.ingress = []
        self.egress = []

    def add_flow(self, receiver, port):
        """
        A function that will open one-way traffic on a specific port from this SecurityEnabledObject to another.
        :param receiver: The SecurityEnabledObject that needs an ingress rule to accept traffic in
        :param port: Port to send, and receive traffic on
        """
        receiver.add_ingress(self, port)
        self.add_egress(receiver, port)

    def add_ingress(self, sender, port):
        """
        Add an ingress rule to this SecurityEnabledObject after evaluating if it is a Security group or CIDR tuple
        ([0] = title, [1] = ip)
        Creates a Troposphere SecurityGroupIngress object
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param sender: The SecurityEnabledObject that will be sending traffic to this SecurityEnabledObject,
        sender[0] = title, sender[1] = ip
        :param port: Port to send, and receive traffic on
        """
        sender_title = sender.title if hasattr(sender, 'title') else sender['name']

        if port == '-1':
            common = {'IpProtocol': 'tcp', 'FromPort': '0', 'ToPort': '65535', 'GroupId': self.security_group}
            name = self.title + 'AllFrom' + sender_title + 'All'
        else:
            common = {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port, 'GroupId': self.security_group}
            name = self.title + port + 'From' + sender_title + port

        ingress = self.template.add_resource(ec2.SecurityGroupIngress(get_cf_friendly_name(name), **common))

        if isinstance(sender, SecurityEnabledObject):
            ingress.SourceSecurityGroupId = sender.security_group
        else:
            ingress.CidrIp = sender['cidr']

        self.ingress.append(ingress)

    def add_egress(self, receiver, port):
        """
        Add an egress rule to this SecurityEnabledObject evaluating if it is a Security group or CIDR tuple
        ([0] = title, [1] = ip)
        Creates a Troposphere SecurityGroupEgress object
        AWS Cloud Formation:
        http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param receiver: The SecurityEnabledObject that will be receiving traffic to this SecurityEnabledObject
        receiver[0] = title, receiver[1] = ip
        :param port: Port to send, and receive traffic on
        """
        receiver_title = receiver.title if hasattr(receiver, 'title') else receiver['name']

        if port == '-1':
            common = {'IpProtocol': 'tcp', 'FromPort': '0', 'ToPort': '65535', 'GroupId': self.security_group}
            name = self.title + 'AllTo' + receiver_title + 'All'
        else:
            common = {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port, 'GroupId': self.security_group}
            name = self.title + port + 'To' + receiver_title + port

        egress = self.template.add_resource(ec2.SecurityGroupEgress(get_cf_friendly_name(name), **common))

        if isinstance(receiver, SecurityEnabledObject):
            egress.DestinationSecurityGroupId = receiver.security_group
        else:
            egress.CidrIp = receiver['cidr']
        self.egress.append(egress)


class RemoteReferenceSecurityEnabledObject(SecurityEnabledObject):
    def __init__(self, template, reference_title):
        """
        Create a security enabled object for referencing an amazonia object in another stack
        :param template: The troposphere template object that will be updated with this object
        :param reference_title: name of target security enabled object to reference
        """
        super(RemoteReferenceSecurityEnabledObject, self).__init__(title=reference_title, template=template)
        self.security_group = ImportValue(reference_title)


class LocalReferenceSecurityEnabledObject(SecurityEnabledObject):
    def __init__(self, template, reference_title):
        """
        Create a security enabled object for referencing an amazonia object in the same stack
        :param template: The troposphere template object that will be updated with this object
        :param reference_title: name of target security enabled object to reference
        """
        super(LocalReferenceSecurityEnabledObject, self).__init__(title=reference_title, template=template)
        self.security_group = Ref(reference_title)


class LocalSecurityEnabledObject(SecurityEnabledObject):
    def __init__(self, template, title, vpc):
        """
        Create a security enabled object
        :param template: The troposphere template object that will be updated with this object
        :param title: the Title of the object eg: unit01ELB, unit01ASG
        :param vpc: reference to VPC object
        """
        super(LocalSecurityEnabledObject, self).__init__(title=title, template=template)

        name = self.title + 'Sg'
        self.trop_security_group = self.template.add_resource(
            ec2.SecurityGroup(
                name,
                GroupDescription='Security group',
                Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', name]))
            ))
        self.trop_security_group.VpcId = vpc

        self.security_group = Ref(self.trop_security_group)
