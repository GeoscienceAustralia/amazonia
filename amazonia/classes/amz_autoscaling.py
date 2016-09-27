#!/usr/bin/python3

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb
from amazonia.classes.leaf import Leaf
from amazonia.classes.security_enabled_object import RemoteReferenceSecurityEnabledObject, \
    LocalReferenceSecurityEnabledObject
from troposphere import Output, GetAtt, ImportValue


class Autoscaling(object):
    def __init__(self, title, template, network_config, elb_config, asg_config, dependencies):
        """
        Create Amazonia Autoscaling resources, an ELB, an autosclaing group and other associated resources
        :param title: title of the amazonia obect and associated resources to be used in cloud formation
        :param template: the troposphere template object to update
        :param network_config: the VPC/subnets etc to deploy autoscaling resources into
        :param elb_config: config related to Elastic Load Balancer
        :param asg_config: config related to AutoScaling Group
        :param dependencies: List of resources to create network flow to
        """
        self.title = title
        self.template = template
        self.loadbalancer_ports = [listener.loadbalancer_port for listener in elb_config.elb_listeners_config]
        self.instance_ports = [listener.instance_port for listener in elb_config.elb_listeners_config]
        self.dependencies = dependencies if dependencies else []

        self.elb = Elb(
            title=title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )
        self.asg = Asg(
            title=title,
            template=self.template,
            network_config=network_config,
            asg_config=asg_config,
            load_balancers=[self.elb.trop_elb]
        )

        if elb_config.public_unit:
            [self.elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport) for loadbalancerport in
             self.loadbalancer_ports]
        [self.elb.add_flow(receiver=self.asg, port=instanceport) for instanceport in self.instance_ports]

        self.asg.add_egress(receiver=network_config.public_cidr, port='-1')  # All Traffic to Nat gateways
        network_config.jump.add_flow(receiver=self.asg, port='22')


class AutoscalingLeaf(Autoscaling, Leaf):
    def __init__(self, leaf_title, template, dependencies, public_cidr, public_hosted_zone_name, cd_service_role_arn,
                 availability_zones, tree_name, elb_config, asg_config, keypair):
        """
        Create autoscaling resources within a cross referenced stack
        :param leaf_title: title of the amazonia leaf and associated resources to be used in cloud formation
        :param public_cidr: public cidr pattern, this can either allow public access or restrict to an organisation
        :param public_hosted_zone_name: the hosted zone name to create R53 records in
        :param cd_service_role_arn: ARN of the code deploy service role
        :param availability_zones: List of availability zones autoscaling resources can use
        :param tree_name: name of cross referenced stack
        :param keypair: keypair to use with autoscaling instances
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param elb_config: config related to Elastic Load Balancer
        :param asg_config: config related to AutoScaling Group
        """
        self.set_tree_config(template=template, availability_zones=availability_zones,
                             tree_name=tree_name)
        self.tree_config.public_hosted_zone_name = public_hosted_zone_name
        self.tree_config.cd_service_role_arn = cd_service_role_arn
        self.tree_config.availability_zones = availability_zones
        self.tree_config.keypair = keypair
        self.tree_config.public_cidr = public_cidr
        self.tree_config.private_hosted_zone_id = ImportValue(self.tree_name + '-PrivateHostedZoneId')
        self.tree_config.private_hosted_zone_domain = ImportValue(self.tree_name + '-PrivateHostedZoneDomain')
        super(AutoscalingLeaf, self).__init__(leaf_title, template, self.tree_config, elb_config, asg_config,
                                              dependencies)

        self.template.add_output(Output(
            'elbSecurityGroup',
            Description='ELB Security group',
            Value=self.elb.security_group,
            Export={'Name': tree_name + '-' + leaf_title + '-SecurityGroup'}
        ))
        self.template.add_output(Output(
            'elbEndpoint',
            Description='Endpoint of the {0} ELB'.format(self.title),
            Value=GetAtt(self.elb.trop_elb, 'DNSName'),
            Export={'Name': tree_name + '-' + leaf_title + '-Endpoint'}
        ))

        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_leaf_sg = RemoteReferenceSecurityEnabledObject(
                template=template,
                reference_title=self.tree_name + '-' + portless_dependency_name + '-SecurityGroup'
            )
            self.asg.add_flow(receiver=target_leaf_sg, port=dependency_port)


class AutoscalingUnit(Autoscaling):
    def __init__(self, unit_title, template, dependencies, stack_config, elb_config, asg_config):
        """
        Create an integrated Amazonia unit, with associated Amazonia ELB and ASG
        :param unit_title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param stack_config: object containing stack network configuration
        :param elb_config: config related to Elastic Load Balancer
        :param asg_config: config related to AutoScaling Group
        """
        super(AutoscalingUnit, self).__init__(unit_title, template, stack_config, elb_config, asg_config,
                                              dependencies)
        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_unit_sg = LocalReferenceSecurityEnabledObject(
                template=template,
                reference_title=portless_dependency_name + 'Sg'
            )
            self.asg.add_flow(receiver=target_unit_sg, port=dependency_port)
