#!/usr/bin/env bash

# https://unix.stackexchange.com/questions/22615/how-can-i-get-my-external-ip-address-in-a-shell-script
wanip=`dig +short myip.opendns.com @resolver1.opendns.com`

pushd $1
echo "To see the plot, visit http://$wanip/errs_cdf.png after the HTTP server starts."
sudo python -m SimpleHTTPServer 80
popd
