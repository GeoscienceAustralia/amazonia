####Usage

To install library locally for the current user, from the amazonia root directory use:

`make install`

Alternatively, you can use:

`pip3 install -e . --user`

Note: this will install all of the dependencies for the project. The dependencies list can be found in the setup.py file in the 'Install Requires:' section.

To generate cloud formation using amazonia, you need to provide two yaml documents. One containing any application specific details and another for the environmental defaults.

Amazonia will read the two yaml documets and give priority to the application specific yaml, meaning that the defaults can be overridden in the application specific yaml if required. Because of this, it is best to set as many defaults as possible to ensure the best functionality out of this library.

See template.yaml for a guide showing all possible yaml variables and the expected types of contents.

if no yaml files are provided, amazonia will read from amazonia/application.yaml and amazonia/defaults.yaml.

Once you have both of your yaml documents, you can run amazonia using the below command

`python3 amazonia/amz.py -y APPLICATION_YAML_LOCATION -d ENVIRONMENTAL_DEFAULT_YAML_LOCATION`

####Examples

Amazonia should be able to create a working stack with minimal changes from a fresh clone. To try this out, in the application.yaml file in the amazonia folder, change the keypair field to a keypair that exists in your AWS space. Then from the amazonia folder, run `python3 amz.py` and then create a stack in AWS using the cloud formation that is generated.

This will create the following resources:

- 1 x Internet Gateway
- 1 x VPC Gateway Attachment
- 1 x Jump Box (for ssh access into your environment)
- 1 x NAT (Internet access from your app server will pass through this)
- 1 x Autoscaling group (min/max 1 instance. This will be your app server)
- 1 x Launch configuration for the above autoscaling group.
- 6 x subnets (3 public, 3 private)
- 1 x Load Balancer
- 4 x security groups (1 for load balancer, 1 for Autoscaling group, 1 for NAT, 1 for Jump box)
- Route tables, routing and security group rules for all of the above.