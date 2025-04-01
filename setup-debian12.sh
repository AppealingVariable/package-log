#!/bin/bash
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install python3.11-venv python3.11-tk python3-keyring
cd "$HOME/.package-log"
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt