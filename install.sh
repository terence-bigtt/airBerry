#!/bin/bash

CONFIG=$1
CMDLINE=$2

if [ $# -ne 2 ]
then
  echo "Usage:"
  echo "sudo install.sh path_to_config.txt path_to_cmdline.txt"
  exit
fi
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


apt update
apt install python3-pip python3-serial -y

`cp $CONFIG $CONFIG.bu`
`cp $CMDLINE $CMDLINE.bu`

echo "===================="
echo "||  Checking SPI  ||"
echo "===================="
if $(sudo cat $CONFIG | grep -q \#dtparam=spi=on)
then
  echo "SPI disabled, enabling"
  sed -i "s/\#dtparam=spi=on/dtparam=spi=on/g" $CONFIG
else
  echo "SPI enabled"
fi

echo "====================="
echo "||  Checking UART  ||"
echo "====================="

if $(sudo cat $CONFIG | grep dtoverlay=pi3-disable-bt)
then
  echo "BT disabled, ensuring UART"
  sed -i "s/console=serial0,115200//g" $CONFIG
else
  echo "Disabling BT and ensuring UART"
  echo "dtoverlay=pi3-disable-bt" >> $CONFIG
  sed -i "s/console=serial0,115200//g" $CMDLINE
fi


sh ./insall-requirements.sh
echo "================================================="
echo "||  Initial configuration done, please reboot  ||"
echo "================================================="