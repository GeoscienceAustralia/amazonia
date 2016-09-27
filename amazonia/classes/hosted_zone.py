#!/usr/bin/python3

from troposphere import route53, Ref, Join
from troposphere.route53 import HostedZoneVPCs


class HostedZone(object):
    def __init__(self, template, domain, vpcs):
        """
        Creates a troposphere HostedZoneVPC object from a troposphere vpc object.
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param template: The cloud formation template to add this hosted zone to.
        :param domain: The domain you would like for your hosted zone. MUST be 'something.something' (eg 'example.com')
        :param vpcs: A list of VPCs to associate this hosted zone with (if none, a public hosted zone is created)
        """

        self.template = template
        self.domain = domain
        self.trop_hosted_zone = self.create_hosted_zone(self.domain, vpcs)

    def create_hosted_zone(self, domain, vpcs):
        """
        Creates a route53 hosted zone object either public (vpcs=None) or private (vpcs=[vpc1,...])
        AWS: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-hostedzone.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/route53.py
        :param domain: The domain you would like for your hosted zone. MUST be 'something.something' (eg 'example.com')
        :param vpcs: A list of VPCs to associate this hosted zone with (if none, a public hosted zone is created)
        """

        hz_type = 'private' if vpcs else 'public'

        hz_config = route53.HostedZoneConfiguration(
            Comment=Join('', [hz_type,
                              ' hosted zone created by Amazonia for stack: ',
                              Ref('AWS::StackName')])
        )

        hz = self.template.add_resource(route53.HostedZone(
            hz_type+'HostedZone',
            HostedZoneConfig=hz_config,
            Name=domain
        ))

        if vpcs:
            hz.VPCs = []
            for vpc in vpcs:
                hz.VPCs.append(HostedZoneVPCs(VPCId=vpc, VPCRegion=Ref('AWS::Region')))

        return hz
