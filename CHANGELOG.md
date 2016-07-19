# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [1.0.31] - 19/07/2016
- Adding db_hdd_size (allocation size) and db_snapshot_id to database class
- Fix jumphost output to specify that it is a URL rather than an EIP.

## [1.0.26] - 18/07/2016
- Updating cloudtrail Class so DependsOn exists within troposphere function rather than outside it.  

## [1.0.23] - 15/07/2016
- Adding SNS class, Unit Tests and System Tests

## [1.0.21] - 13/07/2016
- Adding Dynamo DB Class, Units Tests and Systems Tests

## [1.0.20] - 12/07/2016
- Adding KMS Class, Units Tests and Systems Tests

## [1.0.17] - 08/07/2016
- Adding s3 Class, Unit tests, System tests
- Adding Cloudtrail Class, Unit tests, Systems tests
- Updated yaml to be more consistant
- Updated yaml and tests to be more encompassing
- Removed test inner and intra test stubs (will return soon)
- Updated test_sys_stack_create to allow passing of cloud formation parameters

## [1.0.16] - 07/07/2016
- Updated Hosted_zone_name to be passed at stack level or unit level in yaml as stack_hosted_zone_name or unit_hosted_zone_name
- Updated single_instance to create an elastic IP and a route 53 record set for jump hosts if stack_hosted_zone_name is provided
- Updated 'DependsOn' options for single instance to be passed in rather than assigned after creation.
- Added 'db_name' yaml value to match DBName value in RDS instances.
- Added 'hdd_size' yaml value to change the size of Autoscaling unit instances.

## [1.0.14] - 04/07/2016
- Updated amazonia/test/sys_tests/test_sys_stack_create.py to include cases for CREATE_FAILED, DELETE_FAILED, ROLLBACK_FAILED for create_and_delete_stack()

## [1.0.9] - 30/06/2016
- Fixed some code linting issued in yaml class.
- Updated all amis to point to latest Amazon Linux images

## [1.0.8] - 29/06/2016
- Testing for Release Automation
- 
## [1.0.7] - 29/06/2016
- Testing for Release Automation

## [1.0.6] - 29/06/2016
- Testing for Release Automation

## [1.0.5] - 27/06/2016
- Added /web folder and a web front end + api

## [1.0.4] - 23/06/2016
- Updated cerberus schema: minsize, maxsize can be numbers or strings
- Updated cerberus schema: sns notification types must be list of strings
- Updated unit tests to reflect sns schema change

## [1.0.3] - 22/06/2016
- Added s3 bucket class, system test and unit tests

## [1.0.2] - 20/06/2016
- Changed test_sys_stack_create.py to allow for yaml files to be passed in

## [1.0.1] - 16/06/2016
- Fixing Schema for sns_notification_types to include lists or strings

## [1.0.0] - 15/06/2016
- Adding changelog.md file, editing sonar-properties file to use semantic versioning v1.0.0
- Added public_unit variable for public and private asg unit switching.
