#!/bin/bash

sudo apt update -y
sudo apt upgrade -y

sudo apt install -y python3-pip python3-smbus i2c-tools python3-rpi.gpio git curl

pip install --upgrade pip --break-system-packages
sudo python3 -m pip install RPLCD --break-system-packages
sudo python3 -m pip install pyotp --break-system-packages 
sudo python3 -m pip install qrcode[pil] --break-system-packages
sudo python3 -m pip install pyqrcode --break-system-packages

sudo mkdir -p /etc/keypad_2fa
sudo chmod 700 /etc/keypad_2fa
sudo chown root:root /etc/keypad_2fa

REPO_URL="https://github.com/bmcdonnough/Sys-Admin-Project.git"
PROJECT_DIR="/home/pi/SysAdminProject"

if [ -d "$PROJECT_DIR" ]; then
	cd "$PROJECT_DIR"
	sudo git pull
else
	sudo git clone "$REPO_URL" "PROJECT_DIR"
fi

sudo mkdir -p /etc/keypad_2fa
sudo chmod 700 /etc/keypad_2fa
sudo chown root:root /etc/keypad_2fa
