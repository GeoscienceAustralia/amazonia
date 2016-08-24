#!/usr/bin/python3

from troposphere import cloudfront, Ref, Tags, Template

#from amazonia.classes.cfdistribution import CFDistribution


def main():
    template = Template()

    origin_s3 = template.add_resource(cloudfront.Origin(
            'origins3',
            DomainName='s3.domain.com',
            Id='S3-bucket-id',
            S3OriginConfig=cloudfront.S3Origin(
                OriginAccessIdentity='originaccessid1'
            )
        )
    )

    origin_elb = template.add_resource(cloudfront.Origin(
            'originelb1',
            DomainName='elb.domain.com',
            Id='ELBid',
            CustomOriginConfig=cloudfront.CustomOrigin(
                HTTPPort='80',
                HTTPSPort='443',
                OriginProtocolPolicy='http-only',
                OriginSSLProtocols=['TLSv1','TLSv1.1','TLSv1.2']
            )
        )
    )

    defaultcachebehavior = template.add_resource(cloudfront.DefaultCacheBehavior(
            TargetOriginId='targetoriginid',
            AllowedMethods=['GET','POST'],
            CachedMethods=['GET','POST'],
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=['self'],
            ViewerProtocolPolicy='allow-all',
            MinTTL=0,
            MaxTTL=0,
            DefaultTTL=0,
            SmoothStreaming=False,
        )
    )

    cache_behavior1 = template.add_resource(cloudfront.CacheBehavior(
            'cachebehavior1',
            TargetOriginId='targetoriginid',
            AllowedMethods=['GET','POST'],
            CachedMethods=['GET','POST'],
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=['self'],
            ViewerProtocolPolicy='allow-all',
            MinTTL=0,
            MaxTTL=0,
            DefaultTTL=0,
            PathPattern='/index.html',
            SmoothStreaming=False,
        )
    )

    cache_behavior2 = template.add_resource(cloudfront.CacheBehavior(
            'cachebehavior2',
            TargetOriginId='targetoriginid2',
            AllowedMethods=['GET','POST'],
            CachedMethods=['GET','POST'],
            Compress=False,
            ForwardedValues=cloudfront.ForwardedValues(
                QueryString=False
            ),
            TrustedSigners=['self'],
            ViewerProtocolPolicy='allow-all',
            MinTTL=0,
            MaxTTL=0,
            DefaultTTL=0,
            PathPattern='/login.js',
            SmoothStreaming=False,
        )
    )

    custom_error_response = template.add_resource(cloudfront.CustomErrorResponse(
            'errorresponse',
            ErrorCachingMinTTL=0,
            ErrorCode=404,
            ResponseCode=200,
            ResponsePagePath='404.html',
        )
    )

    georestriction = template.add_resource(cloudfront.GeoRestriction(
            'georestriction',
            Locations=['AU'],
            RestrictionType='whitelist'
        )
    )

    restrictions = template.add_resource(cloudfront.Restrictions(
            'restrictions',
            GeoRestriction=Ref(georestriction)
        )
    )

    viewercertificate = template.add_resource(cloudfront.ViewerCertificate(
            'viewercertificate',
            AcmCertificateArn='arn:aws:acm::123456789012:certificate/Test',
            CloudFrontDefaultCertificate=True,
            IamCertificateId='1234',
            MinimumProtocolVersion='TLSv1',
            SslSupportMethod='sni-only'
        )
    )

    distribution_config = template.add_resource(cloudfront.DistributionConfig(
            'cfdist',
            Aliases=['www.domain.com','domain.com'],
            Comment='SysTestCFDistribution',
            CustomErrorResponses=Ref(custom_error_response),
            DefaultCacheBehavior=Ref(defaultcachebehavior),
            CacheBehaviors=[Ref(cache_behavior1),Ref(cache_behavior2)],
            DefaultRootObject='index.html',
            Enabled=True,
            Origins=[Ref(origin_elb),Ref(origin_s3)],
            PriceClass='PriceClass_All',
            Restrictions=Ref(restrictions),
            ViewerCertificate=Ref(viewercertificate)
        )
    )

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
