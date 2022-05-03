#!/bin/sh
set -e
sudo cp services/hydro.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hydro.service
sudo pip3 install requirements.txt
sudo reboot