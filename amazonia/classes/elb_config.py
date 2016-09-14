class ElbConfig(object):
    def __init__(self, instance_protocol, instance_port, loadbalancer_protocol, loadbalancer_port, elb_health_check,
                 public_unit, elb_log_bucket, ssl_certificate_id, healthy_threshold, unhealthy_threshold,
                 interval, timeout, sticky_app_cookies):
        """
        Simple config class to contain elb related parameters
        :param instance_protocol: instance_protocol for ELB to communicate with webserver
        :param loadbalancer_protocol: loadbalancer_protocol for world to communicate with ELB
        :param instance_port: ports for ELB and webserver to communicate via
        :param loadbalancer_port: ports for public and ELB to communicate via
        :param elb_health_check: path for ELB healthcheck
        :param public_unit: Boolean to determine if the elb scheme will be internet-facing or private
        :param elb_log_bucket: S3 bucket to log access log to
        :param healthy_threshold: Number of consecutive health check successes before marking as Healthy
        :param unhealthy_threshold: Number of consecutive health check successes before marking as Unhealthy
        :param interval: Interval between health checks
        :param timeout: Amount of time during which no response means a failed health check
        :param sticky_app_cookies: List of application cookies used for stickiness

        """
        self.instance_protocol = instance_protocol
        self.loadbalancer_protocol = loadbalancer_protocol
        self.instance_port = instance_port
        self.loadbalancer_port = loadbalancer_port
        self.elb_health_check = elb_health_check
        self.public_unit = public_unit
        self.elb_log_bucket = elb_log_bucket
        self.ssl_certificate_id = ssl_certificate_id
        self.healthy_threshold = healthy_threshold
        self.unhealthy_threshold = unhealthy_threshold
        self.interval = interval
        self.timeout = timeout
        self.sticky_app_cookies = sticky_app_cookies if sticky_app_cookies else []
