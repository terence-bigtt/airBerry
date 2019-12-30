#!/bin/bash

export airberry_user="airberry"
export airberry_home="/home/"$airberry_user
export NOW=date "+%Y%m%d-%H:%m:%S"
export service_name="airberry.service"
export service_path="/etc/systemd/system/"$service_name

if [[ "$EUID" -ne "0" ]]
  then echo "Please run as root"
  exit
fi


bash ./install-airberry.sh
