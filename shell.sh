#!/bin/sh
echo “Hydroponic Code Setup”
sudo cp services/hydro.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hydro.service
sudo pip3 install -r requirements.txt
echo “No olvidar reiniciar el Raspberry”
