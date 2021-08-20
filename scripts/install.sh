sudo apt-get update
sudo apt-get upgrade -y 
sudo apt-get install -y python3-virtualenv 
cd ~
rm -rf touchscreen touchenv
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools
pip install -r touchscreen/requirements.txt
cp ~/touchscreen/scripts/touch.desktop ~/.local/share/applications
mkdir ~/.config/autostart
cp ~/touchscreen/scripts/touch.desktop ~/.config/autostart
reboot
