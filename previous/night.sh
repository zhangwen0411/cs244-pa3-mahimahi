#!/usr/bin/env bash

./run.sh simple < new-websites

pushd mahimahi
sudo git checkout cs244-pa3
sudo make
sudo make install
popd

./run.sh complex < new-websites
