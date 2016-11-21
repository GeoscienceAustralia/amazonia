#!/bin/bash

git config --global user.email $GIT_EMAIL
git config --global user.name $GIT_NAME
git config --global push.default simple
git clone -b integration https://$GIT_USERNAME:$GIT_PASSWORD@$INFRA_REPO
