#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, Output, Join, GetAtt, route53


class Elb(SecurityEnabledObject):
    def __init__(self, title, template, network_config, elb_config):
        """
        Public Class to create an Elastic Loadbalancer in the unit stack environment
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param title: Name of the Cloud formation stack object
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param network_config: object containing network related variables
        :param elb_config: object containing elb related variables
        """
        self.title = title + 'Elb'
        super(Elb, self).__init__(vpc=network_config.vpc, title=self.title, template=template)
        listener_tuples = zip(elb_config.loadbalancer_port,
                              elb_config.instance_port,
                              elb_config.loadbalancer_protocol,
                              elb_config.instance_protocol)
        subnets = network_config.public_subnets if elb_config.public_unit is True else network_config.private_subnets
        self.trop_elb = self.template.add_resource(
            elb.LoadBalancer(self.title,
                             CrossZone=True,
                             # Assume health check against first protocol/instance port pair
                             HealthCheck=elb.HealthCheck(
                                 Target=elb_config.elb_health_check,
                                 HealthyThreshold='10',
                                 UnhealthyThreshold='2',
                                 Interval='300',
                                 Timeout='60'),
                             Listeners=[elb.Listener(LoadBalancerPort=listener_tuple[0],
                                                     Protocol=listener_tuple[2],
                                                     InstancePort=listener_tuple[1],
                                                     InstanceProtocol=listener_tuple[3]) for listener_tuple
                                        in listener_tuples],
                             Scheme='internet-facing' if elb_config.public_unit is True else 'internal',
                             SecurityGroups=[Ref(self.security_group)],
                             Subnets=[Ref(x) for x in subnets],
                             Tags=Tags(Name=self.title)))
        self.trop_elb.DependsOn = network_config.nat.single.title

        for listener in self.trop_elb.Listeners:
            if elb_config.ssl_certificate_id and listener.Protocol == 'HTTPS':
                listener.SSLCertificateId = elb_config.ssl_certificate_id

        if elb_config.elb_log_bucket:
            self.trop_elb.AccessLoggingPolicy = elb.AccessLoggingPolicy(
                EmitInterval='60',
                Enabled=True,
                S3BucketName=elb_config.elb_log_bucket,
                S3BucketPrefix=Join('', [Ref('AWS::StackName'),
                                         '-',
                                         self.title])
            )
        self.elb_r53 = None
        if elb_config.unit_hosted_zone_name:
            self.create_r53_record(elb_config.unit_hosted_zone_name)
        else:
            self.template.add_output(Output(
                self.trop_elb.title,
                Description='URL of the {0} ELB'.format(self.title),
                Value=Join('', ['http://', GetAtt(self.trop_elb, 'DNSName')])
            ))

    def create_r53_record(self, hosted_zone_name):
        """
        Function to create r53 recourdset to associate with ELB
        :param hosted_zone_name: R53 hosted zone to create record in
        """
        self.elb_r53 = self.template.add_resource(route53.RecordSetGroup(
            self.title + 'R53',
            HostedZoneName=hosted_zone_name,
            RecordSets=[route53.RecordSet(
                Name=Join('', [Ref('AWS::StackName'),
                               '-',
                               self.title,
                               '.',
                               hosted_zone_name]),
                AliasTarget=route53.AliasTarget(dnsname=GetAtt(self.trop_elb, 'DNSName'),
                                                hostedzoneid=GetAtt(self.trop_elb, 'CanonicalHostedZoneNameID')),
                Type='A')]))

        self.template.add_output(Output(
            self.trop_elb.title,
            Description='URL of the {0} ELB'.format(self.title),
            Value=Join('', ['http://', self.elb_r53.RecordSets[0].Name])
        ))
