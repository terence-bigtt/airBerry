#!/bin/#!/usr/bin/env bash

sudo apt update
sudo apt install python3-pip python3-serial -y
sudo pip3 install -r ./requirements.txt
wget -q https://git.io/voEUQ -O /tmp/raspap && bash /tmp/raspap

