#!/usr/bin/python3

from troposphere import route53, Ref, Join, GetAtt


class HostedZone(object):
    def __init__(self, template, title, region=None, vpcs=None):
        """

        :param template:
        :param title:
        :param region:
        :param vpcs:
        """

        self.template = template
        self.trop_hosted_zone = self.create_hosted_zone(title, vpcs, region)

    def add_vpc(self, vpc, region):
        """

        :param vpc:
        :param region:
        :return:
        """

        return route53.HostedZoneVPCs(
            'hz'.format(vpc.title),
            VPCId=vpc.title,
            VPCRegion=region
        )

    def create_hosted_zone(self, title, vpcs, region):
        """

        :param title:
        :param vpcs:
        :param region:
        """

        hz_type = 'public' if vpcs is None else 'private'


        hz_config = route53.HostedZoneConfiguration(
            Comment=Join('', [hz_type,
                              ' hosted zone created by Amazonia for stack: ',
                              Ref('AWS::StackName')])
        )

        hz_vpcs = []

        if vpcs:
            for vpc in vpcs:
                hz_vpcs.append(self.add_vpc(vpc, region))

        if not hz_vpcs:
            hz_vpcs = None

        hz_title = '{0}{1}hz'.format(title, hz_type)

        hz = self.template.add_resource(route53.HostedZone(
            hz_title,
            HostedZoneConfig=hz_config,
            Name=title
        ))

        if hz_vpcs is not None:
            hz.VPCs = hz_vpcs

        return hz

    def add_record_set(self, title, ip=None, elb=None):
        """

        :param title:
        :param ip:
        :param elb:
        """

        if ip is None and elb is None:
            raise NoTargetError('Error: Either an ip or an elb must be provided for recordset to point to')

        record = route53.RecordSetType(
            title,
            HostedZoneId=Ref(self.trop_hosted_zone),
            Comment=Join('', ['record set created by Amazonia for stack: ', Ref('AWS::StackName')]),
            Name=Join('', [Ref('AWS::StackName'), '-', title, '.', self.trop_hosted_zone.title]),
            Type='A'
        )

        if ip is not None:
            record.ResourceRecords = [ip]
            record.TTL = '300'
        elif elb is not None:
            record.AliasTarget = route53.AliasTarget(dnsname=GetAtt(elb, 'DNSName'),
                                                     hostedzoneid=GetAtt(elb, 'CanonicalHostedZoneNameID'))
        else:
            raise NoTargetError('Error: Either an ip or an elb must be provided for recordset to point to')

        self.template.add_resource(record)


class NoTargetError(Exception):
    def __init__(self, value):
        """

        :param value:
        """
        self.value = value
