from amazonia.classes.security_enabled_object import RemoteReferenceSecurityEnabledObject
from amazonia.classes.tree_config import TreeConfig
from troposphere import ImportValue


class Leaf(object):
    def __init__(self):
        """
        Create placeholders for leaf specific resources
        """
        self.leaf_title = None
        self.template = None
        self.availability_zones = None
        self.tree_name = None
        self.tree_config = None

    def set_tree_config(self, template, availability_zones, tree_name):
        """
        Instantiate a tree config object based upon a given tree
        :param template: The troposphere template to add resources to.
        :param availability_zones: availability zones to use
        :param tree_name: Name of releated tree
        :return: tree config object
        """
        self.template = template
        self.availability_zones = availability_zones
        self.tree_name = tree_name

        vpc = ImportValue(tree_name + '-VPC')
        jump = RemoteReferenceSecurityEnabledObject(template=template, reference_title=tree_name + '-Jump')
        nat = RemoteReferenceSecurityEnabledObject(template=template, reference_title=tree_name + '-Nat')
        private_hosted_zone_id = ImportValue(tree_name + '-PrivateHostedZoneId')
        private_hosted_zone_domain = ImportValue(tree_name + '-PrivateHostedZoneDomain')
        sns_topic = ImportValue(tree_name + '-SnsTopic')
        public_subnets = []
        for az in self.availability_zones:
            az = az[-1:].upper()
            public_subnets.append(ImportValue(tree_name + '-PublicSubnet-' + az))

        private_subnets = []
        for az in self.availability_zones:
            az = az[-1:].upper()
            private_subnets.append(ImportValue(tree_name + '-PrivateSubnet-' + az))

        self.tree_config = TreeConfig(vpc=vpc,
                                      jump=jump,
                                      nat=nat,
                                      private_subnets=private_subnets,
                                      public_subnets=public_subnets,
                                      sns_topic=sns_topic,
                                      private_hosted_zone_id=private_hosted_zone_id,
                                      private_hosted_zone_domain=private_hosted_zone_domain
                                      )
