#!/bin/bash

sudo apt-get update
sudo apt-get install -y pylint
curl http://repo1.maven.org/maven2/org/codehaus/sonar/runner/sonar-runner-dist/2.4/sonar-runner-dist-2.4.zip -o /tmp/sonar-runner-dist-2.4.zip
sudo mkdir /opt/sonar-runner
sudo unzip /tmp/sonar-runner-dist-2.4.zip -d /opt/sonar-runner
sudo chmod 755 -R /opt/sonar-runner
export PATH=$PATH:/opt/sonar-runner/sonar-runner-2.4/bin
#git clone -b integration $INFRA_REPO
git clone -b dev-aynsof-systestseparation-AUTO-895 $INFRA_REPO
