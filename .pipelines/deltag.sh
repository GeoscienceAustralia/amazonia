#!/bin/bash

for i in `seq 9 30`; do
  echo $i
  #git tag -d v1.4.$i
  git push origin :refs/tags/v1.4.$i
done
