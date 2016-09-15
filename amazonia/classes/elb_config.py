#!/usr/bin/python3


class ElbConfig(object):
    def __init__(self, elb_listeners_config, elb_health_check,
                 public_unit, elb_log_bucket, ssl_certificate_id, healthy_threshold, unhealthy_threshold,
                 interval, timeout, sticky_app_cookies):
        """
        Simple config class to contain elb related parameters
        :param elb_listeners_config: List of ELB listener configs
        :param elb_health_check: path for ELB healthcheck
        :param public_unit: Boolean to determine if the elb scheme will be internet-facing or private
        :param elb_log_bucket: S3 bucket to log access log to
        :param healthy_threshold: Number of consecutive health check successes before marking as Healthy
        :param unhealthy_threshold: Number of consecutive health check successes before marking as Unhealthy
        :param interval: Interval between health checks
        :param timeout: Amount of time during which no response means a failed health check
        :param sticky_app_cookies: List of application cookies used for stickiness

        """
        self.elb_health_check = elb_health_check
        self.public_unit = public_unit
        self.elb_log_bucket = elb_log_bucket
        self.ssl_certificate_id = ssl_certificate_id
        self.elb_listeners_config = elb_listeners_config
        self.healthy_threshold = healthy_threshold
        self.unhealthy_threshold = unhealthy_threshold
        self.interval = interval
        self.timeout = timeout
        self.sticky_app_cookies = sticky_app_cookies if sticky_app_cookies else []
