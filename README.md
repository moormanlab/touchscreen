# touchscreen
Touchscreen Project


# Installation

After installing Raspberry Pi OS

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-virtualenv
cd ~
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools
pip3 install -r touchscreen/requirements.txt
cp ~/touchscreen/scripts/touch.desktop ~/.local/share/applications
mkdir ~/.config/autostart
cp ~/touchscreen/scripts/touch.desktop ~/.config/autostart
reboot
```
