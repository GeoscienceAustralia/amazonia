#!/usr/bin/python3


class NetworkConfig(object):
    def __init__(self, public_cidr, vpc, public_subnets, private_subnets, nat, jump, keypair, cd_service_role_arn,
                 public_hosted_zone_name, private_hosted_zone, nat_highly_available, nat_gateways):
        """
        Simple config class to contain networking related parameters
        :param public_cidr: Public cidr pattern
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param public_subnets: subnets to create ELB in
        :param private_subnets: subnets to autoscale instances in
        :param nat: nat instance for outbound traffic
        :param jump: jump instance for inbound ssh
        :param public_hosted_zone_name: Route53 hosted zone name string for public Route53 record sets
        :param private_hosted_zone: Route53 hosted zone name to add private Route53 record sets
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        :param nat_highly_available: using a nat gateway instead of a NAT
        :param nat_gateways: use nat gateways instead of nat instance for depends on
        """
        self.public_cidr = public_cidr
        self.vpc = vpc
        self.public_subnets = public_subnets
        self.private_subnets = private_subnets
        self.nat = nat
        self.jump = jump
        self.public_hosted_zone_name = public_hosted_zone_name
        self.private_hosted_zone = private_hosted_zone
        self.keypair = keypair
        self.cd_service_role_arn = cd_service_role_arn
        self.nat_highly_available = nat_highly_available
        self.nat_gateways = nat_gateways

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
