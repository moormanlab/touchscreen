# touchscreen
Touchscreen Project

---

## Installation

After installing Raspberry Pi OS

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-virtualenv
cd ~
git clone https://github.com/moormanlab/touchscreen
python3 -m venv touchenv
source ~/touchenv/bin/activate
pip install --upgrade pip setuptools
pip install -r touchscreen/requirements.txt
export CFLAGS=-fcommon
pip3 install rpi.gpio
cp ~/touchscreen/scripts/touch.desktop ~/.local/share/applications
mkdir ~/.config/autostart
cp ~/touchscreen/scripts/touch.desktop ~/.config/autostart
reboot
```

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

