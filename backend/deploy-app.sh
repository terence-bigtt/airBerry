#!/bin/bash

set -x


airberry_user="airberry"
airberry_home="/home/"$airberry_user
NOW=date "+%Y%m%d-%H:%m:%S"
service_name="airberry.service"
service_path="/etc/systemd/system/"$service_name
#sudo echo $airberry_user "ALL=(ALL:ALL) ALL" >> /etc/sudoers

sudo adduser --disabled-password --gecos "" $airberry_user || echo 'cannot create user ${airberry_user}' >> /dev/null
sudo adduser $airberry_user gpio
sudo adduser $airberry_user dialout
sudo adduser $airberry_user spi

cd $airberry_home

sudo rm -rf ./airBerry
sudo mkdir -p .airberry/app
sudo git clone https://github.com/terence-bigtt/airBerry.git
sudo mv -R $airberry_home/airBerry/backend/* $airberry_home/.airberry/app/
sudo rm -rf ./airBerry

sudo chown -R $airberry_user:$airberry_user .airberry
sudo su $airberry_user -c "pip3 install -r .airberry/app/requirements.txt"

### Deploy service auto start
sudo tee -a $service_path > /dev/null <<EOF "[Unit]
Description=Airberry Daemon
After=multi-user.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 ${airberry_home}/.airberry/app/app.py
Restart=on-abort

[Install]
WantedBy=mutli-user.target"
EOF

sudo chmod 644 $service_path
sudo systemctl enable $service_name
sudo systemctl daemon-reload
