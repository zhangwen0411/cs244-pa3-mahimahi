#!/usr/bin/env bash

set -e

runs=5

ts=`date +%s`
folder=reproduce-$ts

./run.sh $folder $runs < some-websites.txt
sudo cat $folder/*.csv | sudo ./plot.py /dev/stdin $folder/errs_cdf.png

./view-result.sh $folder
