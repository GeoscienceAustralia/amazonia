#!/usr/bin/python3


class TreeConfig(object):
    def __init__(self, vpc, public_subnets, private_subnets, nat, jump, private_hosted_zone_id,
                 private_hosted_zone_domain, sns_topic):
        """
        Simple config class to contain networking related parameters
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param public_subnets: subnets to create ELB in
        :param private_subnets: subnets to autoscale instances in
        :param nat: nat instance for outbound traffic
        :param jump: jump instance for inbound ssh
        :param private_hosted_zone_id: Route53 hosted zone name to add private Route53 record sets
        :param private_hosted_zone_domain: Route53 hosted zone name to add private Route53 record sets
        :param sns_topic: SNS topic to send notifications to
        """
        self.vpc = vpc
        self.public_subnets = public_subnets
        self.private_subnets = private_subnets
        self.nat = nat
        self.jump = jump
        self.private_hosted_zone_id = private_hosted_zone_id
        self.private_hosted_zone_domain = private_hosted_zone_domain
        self.sns_topic = sns_topic

        # unfortunate workaround because you cannot create complex strings in CF and refer to them in the same stack
        self.endpoints = {}

    def get_depends_on(self):
        """
        As a tree's network config is already created, the depends on clause for leave's does not need to be populated
        :return: title to use in depends on
        """
        return None
