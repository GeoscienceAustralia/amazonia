#!/bin/bash
# Update Amazonia webservice

aws autoscaling update-auto-scaling-group --auto-scaling-group-name $WEBSERVICE_ASG --max-size 2 --min-size 2 --desired-capacity 2
sleep 60
aws autoscaling update-auto-scaling-group --auto-scaling-group-name $WEBSERVICE_ASG --max-size 1 --min-size 1 --desired-capacity 1
