#! /bin/bash

echo "piedra.service: ## Starting ##" | systemd-cat -p info

cd /home/carlos/club-de-piedras-device/
source env/bin/activate
python main.py

echo "piedra.service: ## Started ##" | systemd-cat -p info
