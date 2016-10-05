# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [1.4.2] - 5/10/2016
- Temporarily locked web front end to v1.3.13 due to troposphere 1.8.2 dependency not being in Pypi yet.

## [1.4.1] - 29/09/2016
- Adding unit tests for tree and leaf config
- Setting default rds size to t2.micro
- Setting default instance size to t2.nano

## [1.3.14] - 27/09/2016
- Created tree/leaf pattern based upon cloudformation cross stack references
- Added permissions for API gateway to invoke Lambda
- Rewrote unit flow method so that cross stack and integral stack references follow a similar pattern
- Due to changes to how network dependencies are set, port numbers need to be specified as part of the dependency
- Due to unit/leaf naming conventions, some cloud formation references will break and stacks will need to be recreated
- Updated stack schema, yaml and tests to reflect new internal amazonia architecture
- Rewrote creation of tests to make it faster and easier to extend amazonia
- Update Cloudfront unit flow to refer to API Gateways and ELBs

## [1.3.13] - 21/09/2016
- Add support for ACM certificates to Cloudfront distributions

## [1.3.12] - 20/09/2016
- Adding sticky app cookie to test_yaml_complete_valid (mmm, sticky app cookie)

## [1.3.10] - 16/09/2016
- Implement Sticky Cookies for ELBs
- Implement single, non-configurable SNS topic to use with all stack alerts

## [1.3.9] - 14/09/2016
- Add extra configuration for ELBs - healthy/unhealthy thresholds, interval, timeout
- Refactor Cloudfront distributions
- Added an Output for the endpoint of each deployment that is created for api gateway units. Storing these in an 'endpoints' list.
- ELB listeners are now a defaultable list of complex objects rather than 4 different arrays (who were implicitly linked)
- YAML loader now allows defaulting of lists of complex objects (elb listeners) and "None-ing" of single complex objects (no examples yet)

## [1.3.8] - 8/09/2016
- Replaced stack parameter stack_hosted_zone_name with public_hosted_zone_name
- Stack now creates a discrete private hosted zone (configurable via private_hosted_zone_name, default 'private.lan.')
- RDS creates R53 record in private hosted zone
- Internal ELBs create R53 records in private hosted zone
- Public ELBs now use stack public_hosted_zone_name, unit_hosted_zone_name removed
- Updated Web App to handle all types of errors a little nicer.
- Add support for OriginPath, forwarded QueryStrings, CustomHeaders to Cloudfront Distributions

## [1.3.6] - 7/09/2016
- Allow for Lambdas to have no dependencies, and for them to have Cloudwatch event triggers
- Added add unit flow function to Api Gateway class to enable lambda unit integration.
- Added deployments to Api Gateway class.

## [1.3.5] - 6/09/2016
- Introduced amz_version for tracking version used for users
- Adding support for lambda units
- Renamed CF resource for PubRT to PubRouteTable. Stacks will need to be recreated
- Renamed CF resource for PriRT to PriRouteTable. Stacks will need to be recreated

## [1.3.4] - 6/09/2016
- Add Forwarded Headers support to Cloudfront distributions
- Added support for Api Gateway creation
- Added new parameter to stack 'nat_highly_available', allowing users to use a classic single nat or one nat_gateway per AZ
- Added new features to network_config object: nat_highly_available, nat_gateways and a function that returns either a single string or list of strings for troposphere resources to use in depends on (ie depends on 'nat' or depends on ['nat gw1', 'nat gw2', 'nat gw3']
- As per suggestions, get_cf_friendly_name now uses a combination of inflection and regex to split words then convert to snek_kes
- Updated block device mapping variable from bdm to block_device_mappings to reflect suggestions from pycharm and sonarqube
- Improved code coverage with encrypted ebs volumes and a bad defaults test

## [1.3.3] - 2/09/2016
- Change Cerberus.ValidationError to Amazonia.Yaml.InvalidYamlValueError
- Added support for Cloudfront distributions
- Updated defaults.yaml for Cloudfront
- Created and updated relevant unit and systems tests

## [1.3.2] - 31/08/2016
- Updated Parameter name for RDS 

## [1.3.1] - 31/08/2016
- Added UpdatePolicy to Autoscaling Groups to ensure changes to autoscaling groups or launch config will correctly update instances.
- Corrected web_app.yaml to the latest format
- Moved DependsOn to inside of the object creation rather than outside of the object
- Added UpdatePolicy to Autoscaling Groups to ensure changes to autoscaling groups or launch config will correctly update instances.
- Corrected web_app.yaml to the latest format
- Added configuration for simple ec2 metric scaling policies
- Changed method that yaml.py interprets complex nested objects
- Restored use of block_devices_config
- Added simple_scaling_policy_config
- Updated relevant unit tests
- Updated relevant systems tests

## [1.3.0] - 24/08/2016
- Introducing SSLCertificateId for ELBs
- Changing path2ping to elb_health_check and making it an explicit health check e.g. /index.html --> HTTP:80/index.html. Updates to app and default yamls required 
- Changing instance_protocol and loadbalancer_protocol to replace protocols. Updates to app and default yamls required 
- Changing loadbalancerports to loadbalancer_port. Updates to app and default yamls required 
- Changing instanceports to instance_port. Updates to app and default yamls required 
- Updated relevant unit tests
- Updated relevant systems tests

## [1.2.7] - 23/08/2016
- Restoring application.yaml
- Updating DBInstanceIdentifer to use unit title without 'Rds'
- Adding test for DBInstanceIdentifer in test_database_unit.py

## [1.2.6] - 23/08/2016
- Creating DBINstance parameter for database unit
- Removing Dbname was passing in a RDS snapshot id

## [1.2.0] - 17/08/2016
- Introducing block device mappings for autoscaling groups, removing hdd_size as a config

## [1.1.3] - 10/08/2016
- Removing unused zd state exception
- Minor fixes to stack unit tests and stack system to reflect changes to zd and db config

## [1.1.1] - 08/08/2016
- Adding new properties to database unit:db_snapshot_id, db_backup_window, db_backup_retention, db_maintenance_window, db_storage_type

## [1.1.0] - 05/08/2016
- Added zd_autoscaling_unit, a single object that provides zero downtime deployments to autoscaling compute instances.
- Refactored the passing of multiple parameters into config objects (network, elb, asg and database) - this is a breaking change as the input yaml structure and cerberus validation rules have changed.
- Updated tests to reflect changes

## [1.0.40] - 29/07/2016
- Updated DB unit tests with working instance type, fixed styling issues
- Added Angelo Pace to .pullapprove.yml

## [1.0.38] - 27/07/2016
- Added Cloudwatch alarm option for NAT instances
- Added 'add_subscription' and 'add_alarm' function to SNS class
- Updated code to fix some QA issues raised by sonarqube
- Corrected database yaml values so that defaults can be correctly overridden (or left out) as expected
- Added James Kingsmill to .pullapprove.yml

## [1.0.34] - 21/07/2016
- Updated Credstash System tests
- Created tests for '-1' port in security enabled object.
- Added Cloudwatch monitoring userdata to single instance class

## [1.0.32] - 20/07/2016
- Updated rules to allow 0-65535 between NAT and ASG's
- Fix jumphost output to specify that it is a URL rather than an EIP.
- Add HostedZone class, with support for public/private hosted zones.
- Updated Stack class to create a VPC supporting private hosted zones.
- Added Cloudtrail and DynamoDB documentation
- Added Credstash class
- Added key rotation for kms and Credstash commands

## [1.0.29] - 19/07/2016
- Adding db_hdd_size (allocation size) and db_snapshot_id to database class

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
