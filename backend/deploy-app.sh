#!/bin/bash

#set -x


airberry_user="airberry"
airberry_home="/home/"$airberry_user
NOW=date "+%Y%m%d-%H:%m:%S"
service_name="airberry.service"
service_path="/etc/systemd/system/"$service_name

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

### Deploy service auto start
echo "[Unit]" > $service_path
echo "Description=Airberry Daemon" >> $service_path
echo "After=multi-user.target" >> $service_path
echo "" >> $service_path
echo "[Service]" >> $service_path
echo "Type=simple" >> $service_path
echo "User=root" >> $service_path
echo "ExecStart=/usr/bin/python" $airberry_home/.airberry/app/app.py >> $service_path
echo "Restart=on-abort" >> $service_path
echo "" >> $service_path
echo "[Install]" >> $service_path
echo "WantedBy=mutli-user.target" >> $service_path

sudo chmod 644 $service_path
sudo systemctl enable $service_name
sudo systemctl daemon-reload

