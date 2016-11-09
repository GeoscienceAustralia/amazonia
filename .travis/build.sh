#!/bin/bash

if [[ $TRAVIS_BRANCH == 'master' ]]
then
  # Run system tests
  echo 'Running systems tests'
else
  # Run unit tests
  nosetests -vv --with-xunit test/unit_tests/*.py
  nosetests --with-xunit --with-coverage --cover-erase --cover-package=amazonia/classes --cover-xml test/unit_tests
  /opt/sonar-runner/sonar-runner-2.4/bin/sonar-runner -Dsonar.login=$SONAR_LOGIN -Dsonar.host.url=$SONAR_HOST
fi
