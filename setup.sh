#!/bin/bash

# Update and upgrade
sudo apt update
sudo apt upgrade -y

# Install necessary packages
sudo apt install -y python3 git python3-venv python3-pip

# Set git configuration
git config --global user.name "YourUsername"
git config --global user.email "your.email@example.com"

# Clone the repository
git clone https://github.com/Radio-active-Boys/MiniProject.git

# Navigate to the project directory
cd MiniProject

# Install and activate the virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install required Python packages
pip3 install keyboard bleak flask pymongo python-dotenv datetime

# Move to the backend directory
cd ScannerAPI/Backend

# Check if the virtual environment is activated
if [[ $VIRTUAL_ENV == "" ]]; then
  echo "Virtual environment is not activated. Please activate it before running the app."
else
  # Run your app
  python app.py
fi
