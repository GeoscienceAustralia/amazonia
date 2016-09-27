#!/usr/bin/python3


class NetworkConfig(object):
    def __init__(self, public_cidr, vpc, public_subnets, private_subnets, nat, jump, keypair, cd_service_role_arn,
                 public_hosted_zone_name, private_hosted_zone_id, private_hosted_zone_domain, nat_highly_available,
                 nat_gateways, sns_topic, availability_zones):
        """
        Simple config class to contain networking related parameters
        :param public_cidr: Public cidr pattern
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param public_subnets: subnets to create ELB in
        :param private_subnets: subnets to autoscale instances in
        :param nat: nat instance for outbound traffic
        :param jump: jump instance for inbound ssh
        :param public_hosted_zone_name: Route53 hosted zone name string for public Route53 record sets
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        :param nat_highly_available: using a nat gateway instead of a NAT
        :param nat_gateways: use nat gateways instead of nat instance for depends on
        :param sns_topic: SNS topic to send notifications to
        :param availability_zones: availability zones to use
        :param private_hosted_zone_domain: domain name of R53 private hosted zone
        :param private_hosted_zone_id: unique id of R53 private hosted zone
        """
        self.public_cidr = public_cidr
        self.vpc = vpc
        self.public_subnets = public_subnets
        self.private_subnets = private_subnets
        self.nat = nat
        self.jump = jump
        self.public_hosted_zone_name = public_hosted_zone_name
        self.private_hosted_zone_id = private_hosted_zone_id
        self.private_hosted_zone_domain = private_hosted_zone_domain
        self.keypair = keypair
        self.cd_service_role_arn = cd_service_role_arn
        self.nat_highly_available = nat_highly_available
        self.nat_gateways = nat_gateways
        self.sns_topic = sns_topic
        self.availability_zones = availability_zones
        # unfortunate workaround because you cannot create complex strings in CF and refer to them in the same stack
        self.endpoints = {}

    def get_depends_on(self):
        """
        Used to set "depends on" clauses in cloud formation, if the vpc has nat gateways, use the first nat gateway,
         otherwise use the NAT instance
        :return: title to use in depends on
        """
        if self.nat_highly_available:
            return [nat_gateway.title for nat_gateway in self.nat_gateways]
        else:
            return self.nat.single.title
