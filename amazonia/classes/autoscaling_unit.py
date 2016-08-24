#!/usr/bin/python3

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb


class AutoscalingUnit(object):
    def __init__(self, unit_title, template, dependencies, network_config, elb_config, asg_config):
        """
        Create an Amazonia unit, with associated Amazonia ELB and ASG
        :param unit_title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param network_config: object containing
        """
        self.template = template
        self.public_cidr = network_config.public_cidr
        self.loadbalancer_ports = elb_config.loadbalancer_ports
        self.dependencies = dependencies if dependencies else []
        self.elb = Elb(
            title=unit_title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )
        self.asg = Asg(
            title=unit_title,
            template=self.template,
            network_config=network_config,
            asg_config=asg_config,
            load_balancers=[self.elb.trop_elb]
        )
        [self.elb.add_ingress(sender=self.public_cidr, port=loadbalancerport) for loadbalancerport in
         self.loadbalancer_ports]
        [self.elb.add_flow(receiver=self.asg, port=instanceport) for instanceport in elb_config.instance_ports]
        self.asg.add_flow(receiver=network_config.nat, port='-1')  # All Traffic between autoscaling groups and Nats
        network_config.jump.add_flow(receiver=self.asg, port='22')

        self.asg.trop_asg.DependsOn = network_config.nat.single.title

    def get_dependencies(self):
        """
        :return: list of other unit's this unit is dependant upon
        """
        return self.dependencies

    def get_destinations(self):
        """
        :return: return the local ELB for destination of other unit's traffic
        """
        return [self.elb]

    def get_inbound_ports(self):
        """
        :return: return list of ports exposed by ELB for routing other unit's traffic
        """
        return self.loadbalancer_ports

    def add_unit_flow(self, receiver):
        """
        Create security group flow from this Amazonia unit's ASG to another unit's destination security group
        :param receiver: Other Amazonia Unit
        """
        for port in receiver.get_inbound_ports():
            for destination in receiver.get_destinations():
                self.asg.add_flow(receiver=destination, port=port)
