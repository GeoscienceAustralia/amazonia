#!/bin/bash
# Runs on any push to master

# Test whether this commit is only a bumpversion
cmpstr="Bump version: "
# Retrieve the most recent commit from the git log
log=`git log --oneline -n 1 | awk '{$1=""; print $0}'`
echo $log

if [[ $log == $cmpstr* ]]
then
  echo 'Bumpversion - not running systems tests'
else
  echo 'Running systems tests'
  .pipelines/systems-tests.sh \
    && \
    .pipelines/bumpversion.sh \
    && \
    .pipelines/update-webservice.sh

  # Update metrics.gadevs.ga
  datetime=`date -u +"%FT%T.000Z"`
  curl -H "Content-Type: application/json" -X POST -d '{"timestamp": "'"$datetime"'", "Application": "Amazonia-Bitbucket", "Environment": "PROD"}' $METRICS_ELK
fi
