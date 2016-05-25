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
