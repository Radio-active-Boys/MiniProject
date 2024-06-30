#!/bin/bash

# Update and upgrade system packages
sudo apt update
sudo apt upgrade -y

# Install necessary packages
sudo apt install -y python3 git python3-pip

# Set Git configuration
git config --global user.name "Vishal-IITJ"
git config --global user.email vishal.k@aptcoder.in

# Clone the project repository
git clone https://github.com/Radio-active-Boys/MiniProject.git

# Download external site packages and move them to the Raspberry Pi Python directory
wget -O site_packages.tar.gz "https://drive.google.com/uc?export=download&id=16De0qRHSMxURdS5kZN9AfhdkiS1x-hE4"
sudo tar -xzvf site_packages.tar.gz -C /usr/lib/python3/dist-packages/

# Install Visual C on Linux
# Download Visual Studio Code & C++
cd ~/Downloads
wget -O code.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
sudo dpkg -i code.deb

# Navigate to the project directory
cd ~/MiniProject

# Install required Python packages
pip install dnspython Flask pymongo asyncio bleach python3-tk pyserial python-dotenv

# Set MongoDB URI environment variable
echo "MONGODB_URI=mongodb+srv://your_username:your_password@cluster1.Opamvyh.mongodb.net/your_database_name?retryWrites=true&w=majority" > ScannerAPI/Backend/.env

# Run the application
cd ScannerAPI/FrontendAppUI
python FinalApp.py



sudo apt-get install python3-tk -y
sudo apt-get install python3-bleak -y
sudo apt-get install python3-bluetooth -y
sudo apt-get install python3-dnspython -y
sudo apt-get install python3-Flask -y
sudo apt-get install python3-pymongo -y
sudo apt-get install python3-asyncio -y
sudo apt-get install python3-bleach -y
sudo apt-get install python3-pyserial -y
sudo apt-get install python3-python-dotenv -y