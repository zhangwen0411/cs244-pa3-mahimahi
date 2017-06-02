#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Please run this script using sudo."
  exit
fi

echo "Installing dependencies..."
apt-get install build-essential git debhelper autotools-dev dh-autoreconf iptables \
protobuf-compiler libprotobuf-dev pkg-config libssl-dev dnsmasq-base ssl-cert libxcb-present-dev \
libcairo2-dev libpango1.0-dev iproute2 apache2-dev apache2-bin iptables dnsmasq-base gnuplot \
iproute2 apache2-api-20120211 libwww-perl

pip install -r requirements.txt

chmod +x chromedriver
cp chromedriver /usr/bin/
