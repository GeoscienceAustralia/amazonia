#!/bin/bash

pip3 install -e . --upgrade
git clone -b $INFRA_BRANCH https://$GIT_USERNAME:$GIT_PASSWORD@$INFRA_REPO

python3 test/sys_tests/test_sys_stack_create.py -y amazonia/application.yaml -d dodo/configuration_code/scripts/amazonia/amazonia/amazonia_ga_defaults.yaml -t testSysStackGA.template -st testSysStackGA &
python3 test/sys_tests/test_sys_stack_create.py -y amazonia/application.yaml -d amazonia/defaults.yaml -s amazonia/schema.yaml -t testSysStack.template -st testSysStack &
python3 test/sys_tests/test_sys_stack_create.py -y dodo/configuration_code/scripts/amazonia/amazonia/amazonia_verbose_example.yaml -d amazonia/defaults.yaml -t testSysStackVerbose.template -st testSysStackVerbose -p '[{"ParameterKey":"db1MasterPassword","ParameterValue":"password123","UsePreviousValue":false},{"ParameterKey":"db1MasterUsername","ParameterValue":"testdbusername","UsePreviousValue":false}]'
