#!/bin/sh
echo “Hydroponic Code Setup”
sudo cp hydro.service /lib/systemd/system/
sudo chmod 664 /lib/systemd/system/hydro.service
sudo chmod 777 /home/pi/Documents/Hydroponic/Module.py
sudo systemctl daemon-reload
sudo systemctl enable hydro.service
sudo pip3 install -r requirements.txt
sudo cat ../crontab.txt  |sudo crontab -
sudo reboot
