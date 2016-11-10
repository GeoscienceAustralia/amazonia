#!/bin/bash

if [[ $TRAVIS_BRANCH == 'master' ]]
then
  # Run system tests
  python3 test/sys_tests/test_sys_stack_create.py \
    -y amazonia/application.yaml \
    -d amazonia/defaults.yaml \
    -s amazonia/schema.yaml \
    -t testSysStack.template \
    -st testSysStack &
  python3 ./test/sys_tests/test_sys_stack_create.py \
    -y amazonia/application.yaml \
    -d ../${bamboo.infra}/configuration_code/scripts/amazonia/amazonia/amazonia_ga_defaults.yaml \
    -t testSysStackGA.template \
    -st testSysStackGA &
  python3 ./test/sys_tests/test_sys_stack_create.py \
    -y ../${bamboo.infra}/configuration_code/scripts/amazonia/amazonia/amazonia_verbose_example.yaml \
    -d amazonia/defaults.yaml \
    -t testSysStackVerbose.template \
    -st testSysStackVerbose \
    -p '[{"ParameterKey":"db1MasterPassword","ParameterValue":"password123","UsePreviousValue":false},{"ParameterKey":"db1MasterUsername","ParameterValue":"testdbusername","UsePreviousValue":false}]'
else
  # Run unit tests
#  nosetests -vv --with-xunit test/unit_tests/*.py
#  nosetests --with-xunit --with-coverage --cover-erase --cover-package=amazonia/classes --cover-xml test/unit_tests
#  /opt/sonar-runner/sonar-runner-2.4/bin/sonar-runner -Dsonar.login=$SONAR_LOGIN -Dsonar.host.url=$SONAR_HOST
  python3 test/sys_tests/test_sys_stack_create.py \
    -y amazonia/application.yaml \
    -d amazonia/defaults.yaml \
    -s amazonia/schema.yaml \
    -t testSysStack.template \
    -st testSysStack &
  python3 test/sys_tests/test_sys_stack_create.py \
    -y amazonia/application.yaml \
    -d dodo/configuration_code/scripts/amazonia/amazonia/amazonia_ga_defaults.yaml \
    -t testSysStackGA.template \
    -st testSysStackGA &
  python3 ./test/sys_tests/test_sys_stack_create.py \
    -y ../${bamboo.infra}/configuration_code/scripts/amazonia/amazonia/amazonia_verbose_example.yaml \
    -d amazonia/defaults.yaml \
    -t testSysStackVerbose.template \
    -st testSysStackVerbose \
    -p '[{"ParameterKey":"db1MasterPassword","ParameterValue":"password123","UsePreviousValue":false},{"ParameterKey":"db1MasterUsername","ParameterValue":"testdbusername","UsePreviousValue":false}]'
fi
