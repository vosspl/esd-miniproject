# ESD: Hiking Watch
## Introduction
This repository 
## 
## Get Started

To create your own Hiking Assistant home set-up, follow these steps:

1. Transfer files from "raspi" folder to Raspberry Pi with Bluetooth. Make sure the packages from requirements.txt are present in your Python environment.
2. Run wserver.py to initialize the webinterface and database. The webinterface will be vailable in your local network at http://YOUR_IP:5000 (e.g. http://192.168.1.2:5000)
3. Using ESP-IDF, flash your LilyGo watch with the PlatformIO-Project in the "lilygo" folder of this project.
4. That's it - you're ready to go. Both watch and the RaspberryPi are configured for automatic connection. Your last hike will always be transferred if the powered on watch is in proximity to the RaspberryPi.