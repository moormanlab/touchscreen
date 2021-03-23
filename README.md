# touchscreen
Touchscreen Project


# Installation

After installing Raspberry Pi OS

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-virtualenv
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools pygame pygame-menu gpiozero rpi.gpio
cp ~/touchscreen/touch.desktop ~/.local/share/applications
```
