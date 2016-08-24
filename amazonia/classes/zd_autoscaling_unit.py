#!/usr/bin/python3
#  pylint: disable=too-many-arguments, line-too-long

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb


class ZdAutoscalingUnit(object):
    def __init__(self, unit_title, template, dependencies, network_config, elb_config, blue_asg_config,
                 green_asg_config):
        """
        Create an Amazonia unit, with associated Amazonia ELB and ASG
        :param unit_title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param network_config: network related paramters including subnet, nat, jump, etc
        :param elb_config: shared elb configuration
        :param blue_asg_config: configuration specific to the blue asg
        :param green_asg_config: configuration specific to the green asg
        """
        self.template = template
        self.dependencies = dependencies if dependencies else []
        self.elb_config = elb_config

        # Create prod and pre elb's
        self.prod_elb = Elb(
            title='prod' + unit_title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )
        self.pre_elb = Elb(
            title='pre' + unit_title,
            template=self.template,
            network_config=network_config,
            elb_config=elb_config
        )

        # create ASGs
        self.blue_asg = Asg(
            title='blue' + unit_title,
            template=self.template,
            network_config=network_config,
            load_balancers=[self.prod_elb.trop_elb],
            asg_config=blue_asg_config
        )
        self.green_asg = Asg(
            title='green' + unit_title,
            template=self.template,
            network_config=network_config,
            load_balancers=[self.pre_elb.trop_elb],
            asg_config=green_asg_config
        )

        # create security group rules to allow communication between the two ELBS to the two ASGs
        [self.prod_elb.add_flow(receiver=self.blue_asg, port=instanceport)
         for instanceport in elb_config.instance_port]
        [self.prod_elb.add_flow(receiver=self.green_asg, port=instanceport)
         for instanceport in elb_config.instance_port]
        [self.pre_elb.add_flow(receiver=self.blue_asg, port=instanceport)
         for instanceport in elb_config.instance_port]
        [self.pre_elb.add_flow(receiver=self.green_asg, port=instanceport)
         for instanceport in elb_config.instance_port]

        # create security group rules to allow traffic from the public to the loadbalancer
        [self.prod_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
         for loadbalancerport in elb_config.loadbalancer_port]
        [self.pre_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
         for loadbalancerport in elb_config.loadbalancer_port]

        # allow outbound traffic to the NAT
        self.green_asg.add_flow(receiver=network_config.nat, port='-1')
        self.blue_asg.add_flow(receiver=network_config.nat, port='-1')

        # allow inbound traffic from the jumphost
        network_config.jump.add_flow(receiver=self.blue_asg, port='22')
        network_config.jump.add_flow(receiver=self.green_asg, port='22')

        self.blue_asg.trop_asg.DependsOn = network_config.nat.single.title
        self.green_asg.trop_asg.DependsOn = network_config.nat.single.title

    def get_dependencies(self):
        """
        :return: list of other unit's this unit is dependant upon
        """
        return self.dependencies

    def get_destinations(self):
        """
        :return: return the local ELB for destination of other unit's traffic
        """
        return [self.prod_elb, self.pre_elb]

    def get_inbound_ports(self):
        """
        :return: return list of ports exposed by ELB for routing other unit's traffic
        """
        return self.elb_config.loadbalancer_port

    def add_unit_flow(self, receiver):
        """
        Create security group flow from this Amazonia unit's ASG to another unit's destination security group
        :param receiver: Other Amazonia Unit
        """
        for port in receiver.get_inbound_ports():
            for destination in receiver.get_destinations():
                self.blue_asg.add_flow(receiver=destination, port=port)
                self.green_asg.add_flow(receiver=destination, port=port)
