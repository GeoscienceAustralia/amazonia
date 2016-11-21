#!/bin/bash

nosetests -vv --with-xunit test/unit_tests/*.py
nosetests --with-xunit --with-coverage --cover-erase --cover-package=amazonia/classes --cover-xml test/unit_tests
sudo /opt/sonar-runner/sonar-runner-2.4/bin/sonar-runner -Dsonar.login=$SONAR_LOGIN -Dsonar.host.url=$SONAR_HOST
