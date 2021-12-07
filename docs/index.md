# Introduction



## Installation instructions

### Prepare microSD card

Download latest Raspberry Pi OS with Desktop image from [Raspberry Pi OS](https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit)
Use [Raspberry Imager](https://www.raspberrypi.org/software/). If you use a Linux system, alternatively you can unzip the downloaded image and then copy it into the microSD card with the following command:
```
sudo dd if=~/PATH_TO_IMAGE/IMAGE_FILE.img of=/deb/sdb bs=4M
```

After this process the SD card should have 2 partitions. `boot` and `rootfs`

In `boot` partition create the (text) file `wpa_suplicant.conf` and add the following information

```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
     ssid="NETWORK_SSID"
     psk="NETWORK_PASSWORD"
     key_mgmt=WPA-PSK
}
```

Where `NETWORD_SSID` is the WiFi Network SSID (Network Name) and `NETWORK_PASSWORD` is the password. This assume the Network has WPA security which is the most common.
For other type of network see [Network](networks.md)

In `boot` partition create an empty text file called `ssh` (without extension)

In `boot` partition create the text file `config.txt` with the following lines

```
raspi-config noinit do_serial 0 1
dtoverlay=disable-bt
enable_uart=1
```

# First Boot

Insert microSD card into Raspberry Pi slot and power up the touchscreen box.

Configure pi welcome screen (language and location)

If the network configuration was successful, the raspberry pi should be connected to WiFi Network.
 
Get ip hovering over WiFi (add pictures to clarify)

Log into the raspberry pi from a computer connected to the same WiFi Network using ssh protocol.
```
ssh pi@IPADDRES
```
The first time you log in, the password is the default password for a raspberry pi: `raspberry`.
For security issues it is highly recommended to change the password.

```
passwd
```

Then run the [install](scripts/install.sh) script which should be downloaded or run the following commands.
```
sudo apt-get update
sudo apt-get upgrade -y 
sudo apt-get install -y python3-virtualenv 
cd ~
rm -rf touchscreen touchenv
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools
export CFLAGS=-fcommon
pip install -r touchscreen/requirements.txt
cp ~/touchscreen/scripts/touch.desktop ~/.local/share/applications
mkdir ~/.config/autostart
cp ~/touchscreen/scripts/touch.desktop ~/.config/autostart
sudo apt-get install libsdl2-mixer-2.0-0 libsdl2-2.0-0
reboot
```
Note: after the first command it might require the password


# Using the software

After rebooting, the touchscreen software should start automatically.


# Troubleshooting

If at any point the raspberry pi is not able to connect to the WiFi network, the network configuration migth be disabled.
The file `/etc/wpa_supplicant/wpa_supplicant.conf` in the `rootfs` partition can have multiple networks configurations loaded.
We should check that the one we need to use does not have the line `disabled=1` added.
