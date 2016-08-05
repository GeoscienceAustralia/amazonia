class NetworkConfig(object):
    def __init__(self, public_cidr, vpc, public_subnets, private_subnets, nat, jump, keypair, cd_service_role_arn,
                 stack_hosted_zone_name):
        """
        Simple config class to contain networking related parameters
        :param public_cidr: Public cidr pattern
        :param vpc: Troposphere vpc object, required for SecurityEnabledObject class
        :param public_subnets: subnets to create ELB in
        :param private_subnets: subnets to autoscale instances in
        :param nat: nat instance for outbound traffic
        :param jump: jump instance for inbound ssh
        :param stack_hosted_zone_name: Route53 hosted zone name string for Route53 record sets
        :param keypair: Instance Keypair for ssh e.g. 'pipeline' or 'mykey'
        :param cd_service_role_arn: AWS IAM Role with Code Deploy permissions
        """
        self.public_cidr = public_cidr
        self.vpc = vpc
        self.public_subnets = public_subnets
        self.private_subnets = private_subnets
        self.nat = nat
        self.jump = jump
        self.stack_hosted_zone_name = stack_hosted_zone_name
        self.keypair = keypair
        self.cd_service_role_arn = cd_service_role_arn
