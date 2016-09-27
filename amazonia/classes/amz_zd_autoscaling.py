#!/usr/bin/python3

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb
from amazonia.classes.leaf import Leaf
from amazonia.classes.security_enabled_object import RemoteReferenceSecurityEnabledObject, \
    LocalReferenceSecurityEnabledObject
from troposphere import Output, GetAtt, ImportValue


class ZdAutoscaling(object):
    def __init__(self, title, template, network_config, elb_config, blue_asg_config,
                 green_asg_config, dependencies):
        """
        Create Amazonia zero downtime Autoscaling resources, two ELBs, two autoscaling groups and other associated
        resources
        :param title: title of the amazonia object and associated resources to be used in cloud formation
        :param template: the troposphere template object to update
        :param network_config: the VPC/subnets etc to deploy zd autoscaling resources into
        :param elb_config: config related to the Elastic Load Balancers
        :param blue_asg_config: config related to the Blue AutoScaling Group
        :param green_asg_config: config related to the Green AutoScaling Group
        :param dependencies: List of resources to create network flow to
        """
        self.title = title
        self.template = template
        self.loadbalancer_ports = [listener.loadbalancer_port for listener in elb_config.elb_listeners_config]
        self.instance_ports = [listener.instance_port for listener in elb_config.elb_listeners_config]
        self.dependencies = dependencies if dependencies else []

        # Create prod and pre elb's
        self.prod_elb = Elb(
            title=self.title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )
        self.pre_elb = Elb(
            title='pre' + self.title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )

        # create ASGs
        self.blue_asg = Asg(
            title='blue' + self.title,
            template=self.template,
            network_config=network_config,
            load_balancers=[self.prod_elb.trop_elb],
            asg_config=blue_asg_config
        )
        self.green_asg = Asg(
            title='green' + self.title,
            template=self.template,
            network_config=network_config,
            load_balancers=[self.pre_elb.trop_elb],
            asg_config=green_asg_config
        )

        self.loadbalancer_ports = [listener.loadbalancer_port for listener in elb_config.elb_listeners_config]
        self.instance_ports = [listener.instance_port for listener in elb_config.elb_listeners_config]

        # create security group rules to allow communication between the two ELBS to the two ASGs
        [self.prod_elb.add_flow(receiver=self.blue_asg, port=instanceport)
         for instanceport in self.instance_ports]
        [self.prod_elb.add_flow(receiver=self.green_asg, port=instanceport)
         for instanceport in self.instance_ports]
        [self.pre_elb.add_flow(receiver=self.blue_asg, port=instanceport)
         for instanceport in self.instance_ports]
        [self.pre_elb.add_flow(receiver=self.green_asg, port=instanceport)
         for instanceport in self.instance_ports]

        # create security group rules to allow traffic from the public to the loadbalancer
        if elb_config.public_unit:
            [self.prod_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
             for loadbalancerport in self.loadbalancer_ports]
            [self.pre_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
             for loadbalancerport in self.loadbalancer_ports]

        # All Traffic to Nat gateways
        self.green_asg.add_egress(receiver=network_config.public_cidr, port='-1')
        self.blue_asg.add_egress(receiver=network_config.public_cidr, port='-1')

        # allow inbound traffic from the jumphost
        network_config.jump.add_flow(receiver=self.blue_asg, port='22')
        network_config.jump.add_flow(receiver=self.green_asg, port='22')


class ZdAutoscalingLeaf(ZdAutoscaling, Leaf):
    def __init__(self, leaf_title, template, dependencies, public_cidr, public_hosted_zone_name, cd_service_role_arn,
                 availability_zones, tree_name, elb_config, blue_asg_config, green_asg_config, keypair):
        """
        Create zd autoscaling resources within a cross referenced stack
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
        :param blue_asg_config: config related to the Blue AutoScaling Group
        :param green_asg_config: config related to the Green AutoScaling Group
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

        super(ZdAutoscalingLeaf, self).__init__(leaf_title, template, self.tree_config, elb_config, blue_asg_config,
                                                green_asg_config, dependencies)

        self.template.add_output(Output(
            'elbEndpoint',
            Description='Endpoint of the {0} ELB'.format(self.title),
            Value=GetAtt(self.prod_elb.trop_elb, 'DNSName'),
            Export={'Name': self.tree_name + '-' + leaf_title + '-Endpoint'}
        ))
        self.template.add_output(Output(
            'elbSecurityGroup',
            Description='ELB Security group',
            Value=self.prod_elb.security_group,
            Export={'Name': self.tree_name + '-' + leaf_title + '-SecurityGroup'}
        ))

        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_leaf_sg = RemoteReferenceSecurityEnabledObject(
                template=template,
                reference_title=self.tree_name + '-' + portless_dependency_name + '-SecurityGroup'
            )
            self.green_asg.add_flow(receiver=target_leaf_sg, port=dependency_port)
            self.blue_asg.add_flow(receiver=target_leaf_sg, port=dependency_port)


class ZdAutoscalingUnit(ZdAutoscaling):
    def __init__(self, unit_title, template, dependencies, stack_config, elb_config, blue_asg_config,
                 green_asg_config):
        """
        Create zd autoscaling resources within an integrated stack
        :param unit_title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param stack_config: object containing stack network configuration
        :param elb_config: config related to Elastic Load Balancer
        :param blue_asg_config: config related to the Blue AutoScaling Group
        :param green_asg_config: config related to the Green AutoScaling Group
        """
        super(ZdAutoscalingUnit, self).__init__(unit_title, template, stack_config, elb_config, blue_asg_config,
                                                green_asg_config,
                                                dependencies)
        for dependency in self.dependencies:
            portless_dependency_name = dependency.split(':')[0]
            dependency_port = dependency.split(':')[1]
            target_unit_sg = LocalReferenceSecurityEnabledObject(
                template=template,
                reference_title=portless_dependency_name + 'Sg'
            )
            self.blue_asg.add_flow(receiver=target_unit_sg, port=dependency_port)
            self.green_asg.add_flow(receiver=target_unit_sg, port=dependency_port)
