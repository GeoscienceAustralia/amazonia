#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import Tags, Ref, Output, Join, GetAtt, route53
import troposphere.elasticloadbalancing as elb


class Elb(SecurityEnabledObject):
    def __init__(self, title, vpc, template, protocols, loadbalancerports, instanceports, path2ping, subnets,
                 gateway_attachment, hosted_zone_name, elb_log_bucket):
        """
        Public Class to create an Elastic Loadbalancer in the unit stack environment
        AWS Cloud Formation: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-elb.html
        Troposphere: https://github.com/cloudtools/troposphere/blob/master/troposphere/elasticloadbalancing.py
        :param title: Name of the Cloud formation stack object
        :param vpc: The vpc object to add the Elastic Loadbalancer to.
        :param template: The troposphere template to add the Elastic Loadbalancer to.
        :param protocols: Single protocol to allow traffic. This must be in CAPITALS e.g.  HTTP, HTTPS, TCP or SSL
        :param loadbalancerports: list of strings representing ports to Listen for traffic on the load balancer.
        :param instanceports: list of strings representing ports for the load balancer to use when talking to instances.
        :param path2ping: Path for the Healthcheck to ping e.g 'index.html' or 'test/test_page.htm'
        :param subnets: List of subnets either [pub_sub_list] if public unit or [pri_sub_list] if private unit
        :param hosted_zone_name: Route53 hosted zone ID
        :param gateway_attachment: Stack's gateway attachment troposphere object
        :param elb_log_bucket: S3 bucket to log access log to
        """
        self.title = title + 'Elb'
        super(Elb, self).__init__(vpc=vpc, title=self.title, template=template)
        network_tuples = zip(loadbalancerports, instanceports, protocols)
        self.trop_elb = self.template.add_resource(
            elb.LoadBalancer(self.title,
                             CrossZone=True,
                             # Assume health check against first protocl/instance port pair
                             HealthCheck=elb.HealthCheck(Target=protocols[0] + ':' + instanceports[0] + path2ping,
                                                         HealthyThreshold='10',
                                                         UnhealthyThreshold='2',
                                                         Interval='300',
                                                         Timeout='60'),
                             Listeners=[elb.Listener(LoadBalancerPort=network_tuple[0],
                                                     Protocol=network_tuple[2],
                                                     InstancePort=network_tuple[1],
                                                     InstanceProtocol=network_tuple[2]) for network_tuple
                                        in network_tuples],
                             Scheme='internet-facing',
                             SecurityGroups=[Ref(self.security_group)],
                             Subnets=[Ref(x) for x in subnets],
                             Tags=Tags(Name=self.title)))
        self.trop_elb.DependsOn = gateway_attachment.title

        if elb_log_bucket:
            self.access_logging_policy = self.trop_elb.AccessLoggingPolicy = elb.AccessLoggingPolicy(
                EmitInterval='60',
                Enabled=True,
                S3BucketName=elb_log_bucket,
                S3BucketPrefix=Join('', [Ref('AWS::StackName'),
                                         '-',
                                         self.title])
            )

        if hosted_zone_name:
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

        else:
            self.template.add_output(Output(
                self.trop_elb.title,
                Description='URL of the {0} ELB'.format(self.title),
                Value=Join('', ['http://', GetAtt(self.trop_elb, 'DNSName')])
            ))
