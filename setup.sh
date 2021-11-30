#!/bin/bashsudo 
apt-get update
apt-get upgrade
apt-get install python3-virtualenv
cd ~
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools
pip install wheel
export CFLAGS=-fcommon
pip3 install -r touchscreen/requirements.txt
apt install libsdl2-ttf-2.0-0
cp ~/touchscreen/scripts/touch.desktop ~/.local/share/applications
mkdir ~/.config/autostart
cp ~/touchscreen/scripts/touch.desktop ~/.config/autostart
reboot
