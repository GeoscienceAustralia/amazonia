#!/usr/bin/python3

import troposphere.elasticloadbalancing as elb
from amazonia.classes.security_enabled_object import LocalSecurityEnabledObject
from troposphere import Tags, Ref, Output, Join, GetAtt, route53


class Elb(LocalSecurityEnabledObject):
    def __init__(self, title, template, network_config, elb_config):
        """
        Public Class to create an Elastic Loadbalancer in the unit stack environment
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param title: Name of the Cloud formation stack object
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param network_config: object containing network related variables
        :param elb_config: object containing elb related variables, including list of listeners (elb_listener_config)
        """
        self.title = title + 'Elb'
        self.elb_r53 = None
        self.elb_config = elb_config
        self.network_config = network_config
        super(Elb, self).__init__(vpc=network_config.vpc, title=title, template=template)
        elb_listeners = elb_config.elb_listeners_config
        subnets = network_config.public_subnets if elb_config.public_unit is True else network_config.private_subnets
        # Create Tags
        tags = Tags(Name=self.title)
        tags += Tags(owner=elb_config.owner)

        # Create ELB
        self.trop_elb = self.template.add_resource(
            elb.LoadBalancer(self.title,
                             CrossZone=True,
                             HealthCheck=elb.HealthCheck(
                                 Target=elb_config.elb_health_check,
                                 HealthyThreshold=elb_config.healthy_threshold,
                                 UnhealthyThreshold=elb_config.unhealthy_threshold,
                                 Interval=elb_config.interval,
                                 Timeout=elb_config.timeout),
                             Listeners=[elb.Listener(LoadBalancerPort=elb_listener.loadbalancer_port,
                                                     Protocol=elb_listener.loadbalancer_protocol,
                                                     InstancePort=elb_listener.instance_port,
                                                     InstanceProtocol=elb_listener.instance_protocol) for elb_listener
                                        in elb_listeners],
                             Scheme='internet-facing' if elb_config.public_unit is True else 'internal',
                             SecurityGroups=[self.security_group],
                             Subnets=subnets,
                             Tags=tags))
        if network_config.get_depends_on():
            self.trop_elb.DependsOn = network_config.get_depends_on()

        # App sticky session cookies
        sticky_app_cookie_policies = []
        # sticky_app_cookie defaults to None, gather listeners that have cookies
        listeners_with_cookies = [listener for listener in elb_listeners if listener.sticky_app_cookie]

        for listener_num, listener in enumerate(listeners_with_cookies):
            policy_name = self.title + 'AppCookiePolicy' + listener.sticky_app_cookie \
                          + str(listener.instance_port) + str(listener.loadbalancer_port) \
                          + str(listener.instance_protocol)

            sticky_app_cookie_policies.append(elb.AppCookieStickinessPolicy(
                CookieName=listener.sticky_app_cookie,
                PolicyName=policy_name
            ))

            # Even though ELB.Listeners.PolicyNames is a List in the cloudformation documentation,
            # it only accepts a single list element, not multiple...
            self.trop_elb.Listeners[listener_num].PolicyNames = [policy_name]

        if sticky_app_cookie_policies:
            self.trop_elb.AppCookieStickinessPolicy = sticky_app_cookie_policies

        # Create SSL for Listeners
        for listener in self.trop_elb.Listeners:
            if elb_config.ssl_certificate_id and listener.Protocol == 'HTTPS':
                listener.SSLCertificateId = elb_config.ssl_certificate_id

        # Create ELB Log Bucket
        if elb_config.elb_log_bucket:
            self.trop_elb.AccessLoggingPolicy = elb.AccessLoggingPolicy(
                EmitInterval='60',
                Enabled=True,
                S3BucketName=elb_config.elb_log_bucket,
                S3BucketPrefix=Join('', [Ref('AWS::StackName'),
                                         '-',
                                         self.title])
            )

        if not elb_config.public_unit:
            self.create_r53_record(network_config.private_hosted_zone_domain)
        elif network_config.public_hosted_zone_name:
            self.create_r53_record(network_config.public_hosted_zone_name)

        else:
            self.template.add_output(Output(
                self.trop_elb.title,
                Description='URL of the {0} ELB'.format(self.title),
                Value=Join('', ['http://', GetAtt(self.trop_elb, 'DNSName')])
            ))

        self.network_config.endpoints[title] = GetAtt(self.trop_elb, 'DNSName')

    def create_r53_record(self, hosted_zone_name):
        """
        Function to create r53 recourdset to associate with ELB
        :param hosted_zone_name: R53 hosted zone to create record in
        """
        if self.elb_config.public_unit:
            name = Join('', [Ref('AWS::StackName'),
                             '-',
                             self.title,
                             '.',
                             hosted_zone_name])
        else:
            name = Join('', [self.title,
                             '.',
                             hosted_zone_name])
        self.elb_r53 = self.template.add_resource(route53.RecordSetGroup(
            self.title + 'R53',
            RecordSets=[route53.RecordSet(
                Name=name,
                AliasTarget=route53.AliasTarget(dnsname=GetAtt(self.trop_elb, 'DNSName'),
                                                hostedzoneid=GetAtt(self.trop_elb, 'CanonicalHostedZoneNameID')),
                Type='A')]))

        if not self.elb_config.public_unit:
            self.elb_r53.HostedZoneId = self.network_config.private_hosted_zone_id
        else:
            self.elb_r53.HostedZoneName = hosted_zone_name

        self.template.add_output(Output(
            self.trop_elb.title,
            Description='URL of the {0} ELB'.format(self.title),
            Value=Join('', ['http://', self.elb_r53.RecordSets[0].Name])
        ))
