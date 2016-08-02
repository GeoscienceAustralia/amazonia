#!/usr/bin/python3

from troposphere import route53, Ref, Join, GetAtt


class HostedZone(object):
    def __init__(self, template, title, domain, vpcs=None):
        """
        Creates a troposphere HostedZoneVPC object from a troposphere vpc object.
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param template: The cloud formation template to add this hosted zone to.
        :param title: A title to give the Hostedzone.
        :param domain: The domain you would like for your hosted zone. MUST be 'something.something' (eg 'example.com')
        :param vpcs: A list of VPCs to associate this hosted zone with (if none, a public hosted zone is created)
        """

        self.template = template
        self.trop_hosted_zone = self.create_hosted_zone(title, domain, vpcs)
        self.recordsets = []

    @staticmethod
    def add_vpc(vpc):
        """
        Creates a troposphere HostedZoneVPC object from a troposphere vpc object.
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone-hostedzonevpcs.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param vpc: A troposphere VPC object
        :return: A route53 HostedZoneVPC object to associate the hosted zone with.
        """

        return route53.HostedZoneVPCs(
            '{0}hz'.format(vpc.title),
            VPCId=Ref(vpc),
            VPCRegion=Ref("AWS::Region")
        )

    def create_hosted_zone(self, title, domain, vpcs):
        """
        Creates a route53 hosted zone object either public (vpcs=None) or private (vpcs=[vpc1,...])
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param title: A title to give the Hostedzone.
        :param domain: The domain you would like for your hosted zone. MUST be 'something.something' (eg 'example.com')
        :param vpcs: A list of VPCs to associate this hosted zone with (if none, a public hosted zone is created)
        """

        hz_type = 'public' if vpcs is None else 'private'

        hz_config = route53.HostedZoneConfiguration(
            Comment=Join('', [hz_type,
                              ' hosted zone created by Amazonia for stack: ',
                              Ref('AWS::StackName')])
        )

        hz_vpcs = []

        if hz_type is 'private':
            for vpc in vpcs:
                hz_vpcs.append(self.add_vpc(vpc))

        if not hz_vpcs:
            hz_vpcs = None

        hz = self.template.add_resource(route53.HostedZone(
            title,
            HostedZoneConfig=hz_config,
            Name=domain
        ))

        if hz_vpcs is not None:
            hz.VPCs = hz_vpcs

        return hz

    def add_record_set(self, title, ip=None, elb=None):
        """
        Creates a route53 recordset to point to either the provided ip or elb.
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param title: A title for the recordset being added to this hostedzone.
        :param ip: An IP for this recordset to point at. Cannot provide 'elb' with this.
        :param elb: An Elastic Loadbalancer for this recordset to point at. Cannot provide 'ip' with this.
        """

        if ip is None and elb is None:
            raise BadTargetError('Error: Either an ip or an elb must be provided for the \
            recordset "{0}" to point to'.format(title))

        if ip is not None and elb is not None:
            raise BadTargetError('Error: An ip and an elb cannot be specified at the same time. \
            Please check objects provided for recordset "{0}"'.format(title))

        record = route53.RecordSetType(
            title,
            HostedZoneId=Ref(self.trop_hosted_zone),
            Comment=Join('', ['record set created by Amazonia for stack: ', Ref('AWS::StackName')]),
            Name=Join('', [title, '.', self.trop_hosted_zone.Name]),
            Type='A'
        )

        if ip is not None:
            record.ResourceRecords = [ip]
            record.TTL = '300'
        elif elb is not None:
            record.AliasTarget = route53.AliasTarget(dnsname=GetAtt(elb, 'DNSName'),
                                                     hostedzoneid=GetAtt(elb, 'CanonicalHostedZoneNameID'))

        self.recordsets.append(record)
        self.template.add_resource(record)


class BadTargetError(Exception):
    def __init__(self, value):
        """
        An error to raise if the user provides Neither or Both ip, and an elb for a recordset to point to.
        :param value: The error message to display to the user.
        """
        self.value = value
