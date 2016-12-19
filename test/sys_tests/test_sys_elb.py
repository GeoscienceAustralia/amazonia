#!/usr/bin/python3

from amazonia.classes.elb import Elb
from amazonia.classes.elb_config import ElbConfig, ElbListenersConfig
from network_setup import get_network_config


def main():
    network_config, template = get_network_config()

    elb_listeners_config = [
        ElbListenersConfig(
            instance_port='80',
            loadbalancer_port='80',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='JSESSION'
        ),
        ElbListenersConfig(
            instance_port='8080',
            loadbalancer_port='8080',
            loadbalancer_protocol='HTTP',
            instance_protocol='HTTP',
            sticky_app_cookie='SESSIONTOKEN'
        )
    ]

    elb_config1 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=False,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        owner='autobots'
    )
    elb_config2 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        ssl_certificate_id='arn:aws:acm::tester',
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        owner='autobots'
    )
    elb_config3 = ElbConfig(
        elb_listeners_config=elb_listeners_config,
        elb_health_check='HTTP:80/index.html',
        elb_log_bucket='my-s3-bucket',
        public_unit=True,
        ssl_certificate_id=None,
        healthy_threshold=10,
        unhealthy_threshold=2,
        interval=300,
        timeout=30,
        owner='autobots'
    )

    Elb(title='MyUnit1',
        network_config=network_config,
        elb_config=elb_config1,
        template=template
        )

    Elb(title='MyUnit2',
        network_config=network_config,
        elb_config=elb_config2,
        template=template
        )
    network_config.public_hosted_zone_name = None
    Elb(title='MyUnit3',
        network_config=network_config,
        elb_config=elb_config3,
        template=template
        )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
