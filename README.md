# touchscreen
Touchscreen Project

---

## Installation

Flash micro SD card with Raspberry Pi OS and insert into Raspberry Pi

On first boot open the Terminal
```bash
sudo raspi-config
````
select `Interface Options` and select and enable 
 - SSH
 - VNC
 - I2C
 - Serial Port
 	- when prompted about a login shell over serial, respond **No**
 	- when promted about serial port hardware, respond **Yes**
 once all Interface Options have been enabled, select Finish

Next, to connect to WiFi run `sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`
and enter the following where `NETWORK_SSID` is your network name and `NETWORK_PASSWORD` is your network password
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
Then run `sudo reboot`

If you are connected, skip to the [setup](#Setup) section

---

**For eudroam**
Instead enter the following in `wpa_supplicant.conf`
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
    ssid="eduroam"
    proto=RSN
    key_mgmt=WPA-EAP
    pairwise=CCMP
    auth_alg=OPEN
    eap=TTLS
    identity="NETID@umass.edu"
    anonymous_identity="NETID@umass.edu"
    password="NETIDPASSWORD"
    phase2="auth=PAP"
}
```
Then enter `sudo nano /etc/wpa_supplicant/functions.sh`

On line 218 change
`WPA_SUP_OPTIONS="$WPA_SUP_OPTIONS -D nl80211,wext"` to `WPA_SUP_OPTIONS="$WPA_SUP_OPTIONS -D wext,nl80211"`

**do the same on line 227** and then save the file

run `sudo reboot`


---

## Setup
Once connected to the internet run
```bash
sudo apt update
sudo apt upgrade -y 
sudo apt install -y python3-virtualenv 
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
sudo apt install libsdl2-mixer-2.0-0 libsdl2-2.0-0 libsdl2-ttf-2.0-0
```
To send data by email create a file called `creds.json` in the `touchscreen` directory
Inside the `creds.json` enter `{"username": "EMAIL", "password": "PASSWORD"}`

*Note for Gmail users*

- Due to changes by Google as of May 30th, 2022, you can no longer use the gmail accounts password in this application.
	- Instead go to google security settings
		- Enable 2-Step Verification
		- Once enabled, select `App passwords` (also in Security settings)
		- under Select app, choose `Mail` and for Select device, Select `Other` and enter a custom name
		- **A popup window will apear with a 16 letter passcode. Enter this for PASSWORD in `creds.json`**

Finally run `sudo reboot` 
Once the device has rebooted with the menu open, select speacial settings and configure the hardware settings as seen fit.

---

## Quick Start Guide

### Main Menu
- Subject Id/Experimenter Id
	- set entity to existing selection using drop-down menu
	- add new entity using the add button next to drop-down
	- selected subject and experimenter are saved in protocol log files
- [Protocols](#Protocol-Menu)
	- brings up new menu containing protocol *modules*
- [Send Data](#Send-Data-Menu)
	- brings up new menu for sending existing log and csv files
- [settings](#Settings-Menu)
	- basic device and software configuration
- [Special Settings](#Special-Settings-Menu)
	- settings to manage logging and hardware

### Protocol Menu
- active subject and experimenter displayed at the top
- each python file in the `protocols` directory is displayed as a button
	- each file should contain at least 1 class based on the provided touchscreen protocol
	- when a protocol module is selected, a new menu will appear with a list of the contained protocols.
		- **when a protocol is selected from this menu, it will execute that protocol**

### Send Data Menu
- Set email address
	- enter email address using the onscreen keyboard
- File
	- scroll through the log/csv files until the desired file is selected
	- click on the **Add file** button
	- multiple files may be attached to one email
- View attached files
	- displays a pop up with attached files
- Send
	- emails the file(s) to the provided email address.
- *under the current system, all log files will be converted to csv files before being attached*

### Settings Menu
- Liquid Reward opens new menu
	- change valve from open to closed
		- useful for initial loading of the pump with liquid reward 
	- Give Drop
	- Drop Open Time
		- open time relates to set_drop_amount method (takes open time in multiples of 10ms)
	- **Give drop and Drop Open time are useful for determining how to set the drop amount in the protocols.**
- Infared Sensor opens new page
	- test IR sensor state
- Sound opens new menu
	- set frequency, amplitude, and duration to test the speaker/buzzer
- Shutdown Device
	- brings up confirmation and powers off touchscreen

### Special Settings Menu
- Logging Level
	- toggle the log files verbosity between debugging mode and info mode
- Synchronize time on start
	- *no function*
- Battery
	- toggle between battery power and continuous power supply
- Audio System
	- toggle between speaker, buzzer, and disable output
- IR Reward Sensor
	- toggle between sparkfun, adafruit, and disable input
- Liquid Reward System
	- change the actuation mechanism (Valve, Pump, None)
- Food Reward System
	- *no function*
- Update Software
	- calls script that pulls the latest version of the main branch

---

