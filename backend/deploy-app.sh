#!/bin/bash

#set -x


airberry_user="airberry"
airberry_home="/home/"$airberry_user
NOW=date "+%Y%m%d-%H:%m:%S"

sudo adduser --disabled-password --gecos "" $airberry_user || echo 'cannot create user ${airberry_user}' >> /dev/null
sudo adduser $airberry_user gpio
sudo adduser $airberry_user dialout
sudo adduser $airberry_user spi

cd $airberry_home

rm -rf ./airBerry
rm -rf .airberry/app
mkdir -p .airberry/app
git clone https://github.com/terence-bigtt/airBerry.git
mv $airberry_home/airBerry/backend/* $airberry_home/.airberry/app/
rm -rf ./airBerry

chown -R $airberry_user:$airberry_user .airberry
sudo su $airberry_user -c "pip3 install -r .airberry/app/requirements.txt"
