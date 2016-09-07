#!/usr/bin/python3

from amazonia.classes.lambda_unit import LambdaUnit
from amazonia.classes.lambda_config import LambdaConfig
from amazonia.classes.network_config import NetworkConfig
from amazonia.classes.single_instance import SingleInstance
from amazonia.classes.single_instance_config import SingleInstanceConfig
from troposphere import ec2, Ref, Tags, Template


def main():
    template = Template()
    vpc = template.add_resource(ec2.VPC('MyVPC',
                                        CidrBlock='10.0.0.0/16'))

    internet_gateway = template.add_resource(ec2.InternetGateway('MyInternetGateway',
                                                                 Tags=Tags(Name='MyInternetGateway')))

    template.add_resource(ec2.VPCGatewayAttachment('MyVPCGatewayAttachment',
                                                   InternetGatewayId=Ref(internet_gateway),
                                                   VpcId=Ref(vpc),
                                                   DependsOn=internet_gateway.title))

    private_subnets = [template.add_resource(ec2.Subnet('MyPubSub1',
                                                        AvailabilityZone='ap-southeast-2a',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.1.0/24')),
                       template.add_resource(ec2.Subnet('MyPubSub2',
                                                        AvailabilityZone='ap-southeast-2b',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.2.0/24')),
                       template.add_resource(ec2.Subnet('MyPubSub3',
                                                        AvailabilityZone='ap-southeast-2c',
                                                        VpcId=Ref(vpc),
                                                        CidrBlock='10.0.3.0/24'))]

    public_subnets = [template.add_resource(ec2.Subnet('MySubnet2',
                                                       AvailabilityZone='ap-southeast-2a',
                                                       VpcId=Ref(vpc),
                                                       CidrBlock='10.0.2.0/24'))]
    single_instance_config = SingleInstanceConfig(
        keypair='pipeline',
        si_image_id='ami-53371f30',
        si_instance_type='t2.nano',
        vpc=vpc,
        subnet=public_subnets[0],
        instance_dependencies=internet_gateway.title,
        alert=None,
        alert_emails=None,
        public_hosted_zone_name=None,
        iam_instance_profile_arn=None,
        is_nat=True
    )
    nat = SingleInstance(title='nat',
                         template=template,
                         single_instance_config=single_instance_config
                         )

    network_config = NetworkConfig(
        public_subnets=None,
        vpc=vpc,
        private_subnets=private_subnets,
        jump=None,
        nat=nat,
        public_cidr=None,
        public_hosted_zone_name=None,
        private_hosted_zone=None,
        keypair=None,
        cd_service_role_arn=None,
        nat_highly_available=False,
        nat_gateways=[]
    )

    lambda_config = LambdaConfig(
        lambda_s3_bucket='blah',
        lambda_s3_key='blah',
        lambda_description='',
        lambda_function_name='',
        lambda_handler='',
        lambda_memory_size=128,
        lambda_role_arn='',
        lambda_runtime='',
        lambda_timeout=1,
        lambda_schedule='cron(0 14 * * *)'
    )

    # Test Lambda
    LambdaUnit(unit_title='MyLambda',
               network_config=network_config,
               template=template,
               dependencies=[],
               lambda_config=lambda_config
               )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
