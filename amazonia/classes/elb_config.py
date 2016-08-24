class ElbConfig(object):
    def __init__(self, protocols, instanceports, loadbalancerports, elb_health_check, public_unit, elb_log_bucket,
                 unit_hosted_zone_name, ssl_certificate_id):
        """
        Simple config class to contain elb related parameters
        :param protocols: protocols for ELB and webserver to communicate via
        :param instanceports: ports for ELB and webserver to communicate via
        :param loadbalancerports: ports for public and ELB to communicate via
        :param elb_health_check: path for ELB healthcheck
        :param public_unit: Boolean to determine if the elb scheme will be internet-facing or private
        :param elb_log_bucket: S3 bucket to log access log to
        :param unit_hosted_zone_name: Route53 hosted zone name string for Route53 record sets
        """
        self.protocols = protocols
        self.instanceports = instanceports
        self.loadbalancerports = loadbalancerports
        self.elb_health_check = elb_health_check
        self.public_unit = public_unit
        self.elb_log_bucket = elb_log_bucket
        self.unit_hosted_zone_name = unit_hosted_zone_name
        self.ssl_certificate_id = ssl_certificate_id
