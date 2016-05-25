#!/usr/bin/python3

from amazonia.classes.security_enabled_object import SecurityEnabledObject
from troposphere import ec2, Template


def main():
    template = Template()
    myvpc = template.add_resource(ec2.VPC('myVpc', CidrBlock='10.0.0.0/16'))
    home_cidrs = [{'name': 'GA1', 'cidr': '123.123.132.123/24'},
                  {'name': 'GA2', 'cidr': '231.231.231.231/32'}]
    public_cidr = {'name': 'PublicIp', 'cidr': '0.0.0.0/0'}

    seo0_jump = SecurityEnabledObject(title="StackJump", vpc=myvpc, template=template)
    seo1_nat = SecurityEnabledObject(title="StackNAT", vpc=myvpc, template=template)
    seo2_web = SecurityEnabledObject(title="Unit01Web", vpc=myvpc, template=template)
    seo3_api = SecurityEnabledObject(title="Unit01Api", vpc=myvpc, template=template)
    seo4_elb = SecurityEnabledObject(title="Unit01Elb", vpc=myvpc, template=template)

    # Add inbound SSH traffic to jump box
    for cidr in home_cidrs:
        seo0_jump.add_ingress(cidr, '22')

    # Add traffic from nat to web and api boxes
    seo1_nat.add_flow(seo2_web, '80')
    seo1_nat.add_flow(seo2_web, '443')
    seo1_nat.add_flow(seo3_api, '80')
    seo1_nat.add_flow(seo3_api, '443')

    # Add traffic from web and api boxes to nat
    seo2_web.add_flow(seo1_nat, '80')
    seo2_web.add_flow(seo1_nat, '443')
    seo3_api.add_flow(seo1_nat, '80')
    seo3_api.add_flow(seo1_nat, '443')

    # Add traffic out of nat to public
    seo1_nat.add_egress(public_cidr, '80')
    seo1_nat.add_egress(public_cidr, '443')

    # Add traffic from elb to web
    seo4_elb.add_flow(seo2_web, '80')
    seo4_elb.add_flow(seo2_web, '443')

    # Add traffic from public to elb
    seo4_elb.add_ingress(public_cidr, '80')
    seo4_elb.add_ingress(public_cidr, '443')

    # Add traffic from web to api
    seo2_web.add_flow(seo3_api, '80')
    seo2_web.add_flow(seo3_api, '443')

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
