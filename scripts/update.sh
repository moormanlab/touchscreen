#!/bin/bash
source /home/pi/touchenv/bin/activate
cd /home/pi/touchscreen/
git reset --hard HEAD
git checkout main
git pull
pip install --upgrade pip setuptools
pip install --upgrade -r /home/pi/touchscreen/requirements.txt
