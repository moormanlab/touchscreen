# touchscreen
Touchscreen Project


# Installation

after installing raspberry OS

sudo apt-get  install python3-virtualenv
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools pygame pygame-menu gpiozer rpi.gpio
cp ~/touchscreen/touch.desktop ~/.local/share/applications
