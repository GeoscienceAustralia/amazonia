#!/usr/bin/python3
#  pylint: disable=too-many-arguments, line-too-long

from amazonia.classes.asg import Asg
from amazonia.classes.elb import Elb


class ZdtdAutoscalingUnit(object):
    def __init__(self, unit_title, template, dependencies, zdtd_state, network_config, elb_config, common_asg_config,
                 blue_asg_config, green_asg_config):
        """
        Create an Amazonia unit, with associated Amazonia ELB and ASG
        :param unit_title: Title of the autoscaling application  prefixedx with Stack name e.g 'MyStackWebApp1',
         'MyStackApi2' or 'MyStackDataprocessing'
        :param template: Troposphere template to append resources to
        :param dependencies: list of unit names this unit needs access to
        :param zdtd_state: blue, green, both
        :param network_config: network related paramters including subnet, nat, jump, etc
        :param elb_config: shared elb configuration
        :param common_asg_config: default asg configuration
        :param blue_asg_config: configuration specific to the blue asg
        :param green_asg_config: configuration specific to the green asg
        """
        self.template = template
        self.dependencies = dependencies if dependencies else []
        self.elb_config = elb_config
        self.prod_elb = Elb(
            vpc=network_config.vpc,
            title='active' + unit_title,
            template=self.template,
            protocols=elb_config.protocols,
            instanceports=elb_config.instanceports,
            loadbalancerports=elb_config.loadbalancerports,
            path2ping=elb_config.path2ping,
            subnets=network_config.public_subnets if elb_config.public_unit is True else network_config.private_subnets,
            hosted_zone_name=network_config.unit_hosted_zone_name,
            gateway_attachment=network_config.nat.single,
            elb_log_bucket=elb_config.elb_log_bucket,
            public_unit=elb_config.public_unit
        )
        self.test_elb = Elb(
            vpc=network_config.vpc,
            title='inactive' + unit_title,
            template=self.template,
            protocols=elb_config.protocols,
            instanceports=elb_config.instanceports,
            loadbalancerports=elb_config.loadbalancerports,
            path2ping=elb_config.path2ping,
            subnets=network_config.public_subnets if elb_config.public_unit is True else network_config.private_subnets,
            hosted_zone_name=network_config.unit_hosted_zone_name,
            gateway_attachment=network_config.nat.single,
            elb_log_bucket=elb_config.elb_log_bucket,
            public_unit=elb_config.public_unit
        )
        if zdtd_state not in ['blue', 'green', 'both']:
            raise InvalidZDTDStateError('zdtd_state must be blue, green or both')

        blue_load_balancers = []
        green_load_balancers = []

        if zdtd_state == 'blue':
            blue_load_balancers.append(self.prod_elb.trop_elb)
            green_load_balancers.append(self.test_elb.trop_elb)
        if zdtd_state == 'green':
            green_load_balancers.append(self.prod_elb.trop_elb)
            blue_load_balancers.append(self.test_elb.trop_elb)
        if zdtd_state == 'both':
            blue_load_balancers.append(self.prod_elb.trop_elb)
            blue_load_balancers.append(self.test_elb.trop_elb)
            green_load_balancers.append(self.prod_elb.trop_elb)
            green_load_balancers.append(self.test_elb.trop_elb)

        blue_asg_config.define_undefined_values(common_asg_config)
        green_asg_config.define_undefined_values(common_asg_config)
        self.blue_asg = Asg(
            vpc=network_config.vpc,
            title='blue' + unit_title,
            template=self.template,
            subnets=network_config.private_subnets,
            minsize=blue_asg_config.minsize,
            maxsize=blue_asg_config.maxsize,
            keypair=blue_asg_config.keypair,
            image_id=blue_asg_config.image_id,
            instance_type=blue_asg_config.instance_type,
            health_check_grace_period=blue_asg_config.health_check_grace_period,
            health_check_type=blue_asg_config.health_check_type,
            userdata=blue_asg_config.userdata,
            load_balancers=blue_load_balancers,
            cd_service_role_arn=blue_asg_config.cd_service_role_arn,
            iam_instance_profile_arn=blue_asg_config.iam_instance_profile_arn,
            sns_topic_arn=blue_asg_config.sns_topic_arn,
            sns_notification_types=blue_asg_config.sns_notification_types,
            hdd_size=blue_asg_config.hdd_size
        )
        self.green_asg = Asg(
            vpc=network_config.vpc,
            title='green' + unit_title,
            template=self.template,
            subnets=network_config.private_subnets,
            minsize=green_asg_config.minsize,
            maxsize=green_asg_config.maxsize,
            keypair=green_asg_config.keypair,
            image_id=green_asg_config.image_id,
            instance_type=green_asg_config.instance_type,
            health_check_grace_period=green_asg_config.health_check_grace_period,
            health_check_type=green_asg_config.health_check_type,
            userdata=green_asg_config.userdata,
            load_balancers=green_load_balancers,
            cd_service_role_arn=green_asg_config.cd_service_role_arn,
            iam_instance_profile_arn=green_asg_config.iam_instance_profile_arn,
            sns_topic_arn=green_asg_config.sns_topic_arn,
            sns_notification_types=green_asg_config.sns_notification_types,
            hdd_size=green_asg_config.hdd_size
        )

        if zdtd_state == 'blue':
            [self.prod_elb.add_flow(receiver=self.blue_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
            [self.test_elb.add_flow(receiver=self.green_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
        if zdtd_state == 'green':
            [self.prod_elb.add_flow(receiver=self.green_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
            [self.test_elb.add_flow(receiver=self.blue_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
        if zdtd_state == 'both':
            [self.prod_elb.add_flow(receiver=self.blue_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
            [self.prod_elb.add_flow(receiver=self.green_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
            [self.test_elb.add_flow(receiver=self.blue_asg, port=instanceport)
             for instanceport in elb_config.instanceports]
            [self.test_elb.add_flow(receiver=self.green_asg, port=instanceport)
             for instanceport in elb_config.instanceports]

        [self.prod_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
         for loadbalancerport in elb_config.loadbalancerports]
        [self.test_elb.add_ingress(sender=network_config.public_cidr, port=loadbalancerport)
         for loadbalancerport in elb_config.loadbalancerports]
        self.green_asg.add_flow(receiver=network_config.nat, port='-1')
        self.blue_asg.add_flow(receiver=network_config.nat, port='-1')
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
        return [self.prod_elb, self.test_elb]

    def get_inbound_ports(self):
        """
        :return: return list of ports exposed by ELB for routing other unit's traffic
        """
        return self.elb_config.loadbalancerports

    def add_unit_flow(self, receiver):
        """
        Create security group flow from this Amazonia unit's ASG to another unit's destination security group
        :param receiver: Other Amazonia Unit
        """
        for port in receiver.get_inbound_ports():
            for destination in receiver.get_destinations():
                self.blue_asg.add_flow(receiver=destination, port=port)
                self.green_asg.add_flow(receiver=destination, port=port)


class InvalidZDTDStateError(Exception):
    def __init__(self, value):
        self.value = value
