#!/usr/bin/env bash

sudo sysctl -w net.ipv4.ip_forward=1   # Enable IP forwarding for Mahimahi.

# Set up X virtual framebuffer for Selenium & Chrome to work.
sudo killall Xvfb 2> /dev/null
sudo Xvfb :99 -ac -noreset &
export DISPLAY=:99

# Run the experiment!
sudo ./run.py $USER
