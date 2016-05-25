#!/usr/bin/python3

from troposphere import ec2, Ref, Tags, GetAtt, Join


class SecurityEnabledObject(object):
    def __init__(self, template, title, vpc):
        """
        A Class to enable uni-directional flow when given two security groups
        :param template: The troposphere template object that will be updated with this object
        :param vpc: The VPC for this object
        :param title: the Title of the object eg: unit01ELB, unit01ASG
        :return: a security group, and the ability to create ingress and egress rules
        """

        self.template = template
        self.title = title
        self.security_group = self.create_security_group(vpc)
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
        Add an ingress rule to this SecurityEnabledObject after evaluating if it is a Security group or CIDR tuple ([0] = title, [1] = ip)
        Creates a Troposphere SecurityGroupIngress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-ingress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param sender: The SecurityEnabledObject that will be sending traffic to this SecurityEnabledObject, sender[0] = title, sender[1] = ip
        :param port: Port to send, and receive traffic on
        """

        common = {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port, 'GroupId': Ref(self.security_group)}

        if isinstance(sender, SecurityEnabledObject):
            name = self.title + port + 'From' + sender.title + port
            self.ingress.append(self.template.add_resource(ec2.SecurityGroupIngress(
                name,
                SourceSecurityGroupId=GetAtt(sender.security_group.title, 'GroupId'),
                **common
                )))
        else:
            name = self.title + port + 'From' + sender['name'] + port
            self.ingress.append(self.template.add_resource(ec2.SecurityGroupIngress(
                name,
                CidrIp=sender['cidr'],
                **common
                )))

    def add_egress(self, receiver, port):
        """
        Add an egress rule to this SecurityEnabledObject evaluating if it is a Security group or CIDR tuple ([0] = title, [1] = ip)
        Creates a Troposphere SecurityGroupEgress object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-security-group-egress.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param receiver: The SecurityEnabledObject that will be receiving traffic to this SecurityEnabledObject receiver[0] = title, receiver[1] = ip
        :param port: Port to send, and receive traffic on
        """

        common = {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port, 'GroupId': Ref(self.security_group)}

        if isinstance(receiver, SecurityEnabledObject):
            name = self.title + port + 'To' + receiver.title + port
            self.egress.append(self.template.add_resource(ec2.SecurityGroupEgress(
                name,
                DestinationSecurityGroupId=GetAtt(receiver.security_group.title, 'GroupId'),
                **common
                )))
        else:
            name = self.title + port + 'To' + receiver['name'] + port
            self.egress.append(self.template.add_resource(ec2.SecurityGroupEgress(
                name,
                CidrIp=receiver['cidr'],
                **common
                )))

    def create_security_group(self, vpc):
        """
        Add a security group to this SecurityEnabledObject which can then have rules added to it where needed
        Creates a Troposphere SecurityGroup object
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group.html
        Troposphere link: https://github.com/cloudtools/troposphere/blob/master/troposphere/ec2.py
        :param vpc: The VPC that the security group should live in
        :return: The troposphere security group object for this SecurityEnabledObject
        """
        name = self.title + 'Sg'
        return self.template.add_resource(
                    ec2.SecurityGroup(
                        name,
                        GroupDescription='Security group',
                        VpcId=Ref(vpc),
                        Tags=Tags(Name=Join('', [Ref('AWS::StackName'), '-', name]))
                        ))
