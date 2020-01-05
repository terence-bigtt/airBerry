#!/bin/bash

set -x

cd $airberry_home

sudo rm -rf ./airBerry
sudo git clone https://github.com/terence-bigtt/airBerry.git
sudo rm -rf /airberry/app
sudo mkdir -p .airberry/app
sudo cp -rf $airberry_home/airBerry/backend/* $airberry_home/.airberry/app/
sudo cp -rf $airberry_home/airBerry/ui/dist/* /var/www/html/air
sudo rm -rf $airberry_home/airBerry

sudo chown -R $airberry_user:$airberry_user .airberry
sudo su $airberry_user -c "pip3 install -r .airberry/app/requirements.txt"
sudo apt install gunicorn3 -y


### Deploy service auto start
sudo tee $service_path > /dev/null <<EOF
[Unit]
Description=Airberry Daemon
After=network.target
After = network.target

[Service]
Type=simple
PermissionsStartOnly = true
PIDFile = /run/airberry/app.pid
User=${airberry_user}
Group=${airberry_user}
WorkingDirectory = /home/airberry/.airberry/app
ExecStartPre = /bin/mkdir /run/airberry
ExecStartPre = /bin/chown -R $airberry_user:$airberry_user /run/airberry
Environment=FLASK_ENV=production
ExecStart = /usr/bin/gunicorn3 -w 1 app:app -b 0.0.0.0:5000 --pid /run/airberry/app.pid
ExecReload = /bin/kill -s HUP $MAINPID
ExecStop = /bin/kill -s TERM $MAINPID
ExecStopPost = /bin/rm -rf /run/airberry
Restart=always
RestartSec=10
StandardOutput=append:/var/log/airberry.log

[Install]
WantedBy = multi-user.target
EOF

sudo chmod 644 $service_path
sudo systemctl enable $service_name
sudo systemctl daemon-reload
sudo systemctl restart $service_name
