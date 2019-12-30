#!/bin/bash

set -x

cd $airberry_home

sudo rm -rf ./airBerry
sudo mkdir -p .airberry/app
sudo git clone https://github.com/terence-bigtt/airBerry.git
sudo mv -R $airberry_home/airBerry/backend/* $airberry_home/.airberry/app/
sudo cp -rf $airberry_home/airBerry/ui/dist/* /var/www/html/air
sudo rm -rf $airberry_home/airBerry

sudo chown -R $airberry_user:$airberry_user .airberry
sudo su $airberry_user -c "pip3 install -r .airberry/app/requirements.txt"

### Deploy service auto start
sudo tee -a $service_path > /dev/null <<EOF "[Unit]
Description=Airberry Daemon
After=multi-user.target

[Service]
Type=simple
User=${airberry_user}
ExecStart=/usr/bin/python3 ${airberry_home}/.airberry/app/app.py
Restart=on-failure

[Install]
WantedBy=mutli-user.target"
EOF

sudo chmod 644 $service_path
sudo systemctl enable $service_name
sudo systemctl daemon-reload
sudo sustemctl restart $service_name
