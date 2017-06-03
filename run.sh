#!/usr/bin/env bash

# Set up X virtual framebuffer for Selenium & Chrome to work.
sudo killall Xvfb 2> /dev/null
sudo Xvfb :99 -ac -noreset &
export DISPLAY=:99

# Run the experiment!
sudo ./run.py $USER
