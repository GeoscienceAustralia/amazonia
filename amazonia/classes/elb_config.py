class ElbConfig(object):
    def __init__(self, protocols, instanceports, loadbalancerports, path2ping, public_unit, elb_log_bucket):
        """
        Simple config class to contain elb related parameters
        :param protocols: protocols for ELB and webserver to communicate via
        :param instanceports: ports for ELB and webserver to communicate via
        :param loadbalancerports: ports for public and ELB to communicate via
        :param path2ping: path for ELB healthcheck
        :param public_unit: Boolean to determine if the elb scheme will be internet-facing or private
        :param elb_log_bucket: S3 bucket to log access log to
        """
        self.protocols = protocols
        self.instanceports = instanceports
        self.loadbalancerports = loadbalancerports
        self.path2ping = path2ping
        self.public_unit = public_unit
        self.elb_log_bucket = elb_log_bucket
