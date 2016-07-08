from troposphere import Template, Join

from amazonia.classes.s3 import S3


def main():
    """
    Creates a troposphere template and then adds a single s3 bucket
    """
    template = Template()
    s3_title = 'MyBucket'
    access_control = 'PublicRead'

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": "arn:aws:s3:::mycloudtrailamzs3"
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": Join('', ["arn:aws:s3:::",
                                      s3_title,
                                      "/cloudtrail/AWSLogs/",
                                      {'Ref': 'AWS::AccountId'},
                                      "/*"]),
                "Condition": {
                    "StringEquals": {
                        "s3:x-amz-acl": "bucket-owner-full-control"
                    }
                }
            }
        ]
    }

    S3(unit_title=s3_title,
       template=template,
       s3_access=access_control,
       bucket_policy=policy)

    print(template.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
