#!/bin/bash
#sudo echo $airberry_user "ALL=(ALL:ALL) ALL" >> /etc/sudoers

sudo adduser --disabled-password --gecos "" $airberry_user || echo 'cannot create user ${airberry_user}' >> /dev/null
sudo adduser $airberry_user gpio
sudo adduser $airberry_user dialout
sudo adduser $airberry_user spi


