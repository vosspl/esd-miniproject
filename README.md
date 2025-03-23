# ESD: Hiking Watch

## Demo

<iframe width="560" height="315" src="https://vimeo.com/1068663515/747af03068" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Introduction

This repository contains code for a hiking assistant watch (LilyGo) and a hub with a web interface that stores past
hikes. The hub is supposed to be run on a Raspberry Pi and automatically synchronizes with the watch via Bluetooth.

The system automatically calculates calories burned based on steps taken during hiking sessions and presents the data in
an intuitive dashboard.

## Features

- Real-time Bluetooth synchronization with wearable devices
- Automatic calorie calculation based on METs (Metabolic Equivalent of Task)
- Persistent storage of hiking sessions using SQLite
- Web interface for viewing hiking data with responsive design
- Session management (view details, delete sessions)
- Debug interface to manually add hiking sessions
- Progress visualization with dynamic color-coded charts
- Auto-refresh functionality to display the latest data

## Requirements

### Raspberry Pi Hub

- Python 3.6+
- Flask 1.1.2
- PyBluez 0.23
- SQLite3 (built into Python)

### LilyGo Watch

- ESP32 platform
- Bluetooth enabled

## Hardware Setup

- **LilyGo Watch**: The project is configured for T-Watch 2020 V3 (configurable in config.h)
- **Raspberry Pi**: Any model with Bluetooth capability

## Get Started

To create your own Hiking Assistant home set-up, follow these steps:

1. Transfer files from "raspi" folder to Raspberry Pi with Bluetooth. Make sure the packages from requirements.txt are
   present in your Python environment.
2. Run wserver.py to initialize the webinterface and database. The webinterface will be vailable in your local network
   at http://YOUR_IP:5000 (e.g. http://192.168.1.2:5000)
3. Using ESP-IDF, flash your LilyGo watch with the PlatformIO-Project in the "lilygo" folder of this project.
4. That's it - you're ready to go. Both watch and the RaspberryPi are configured for automatic connection. Your last
   hike will always be transferred if the powered on watch is in proximity to the RaspberryPi.

## How It Works

### Watch Functionality

1. The watch initializes with a welcome screen prompting the user to start a hiking session
2. When the side button is pressed, a new hiking session starts
3. During the hike, the watch tracks:
    - Steps taken (using the built-in BMA423 accelerometer)
    - Distance traveled (calculated from steps)
4. Session data is stored in LittleFS with separate files for:
    - Session ID (`/id.txt`)
    - Step count (`/steps.txt`)
    - Distance (`/distance.txt`)
5. When in proximity to the hub, the watch automatically connects via Bluetooth
6. Upon connection, the watch sends the stored session data to the hub
7. After confirmation from the hub, the watch clears the session data

### Hub Functionality

1. The Raspberry Pi continuously scans for the watch's Bluetooth signal
2. When connected, it requests the latest hiking session data
3. The data is processed and stored in an SQLite database
4. The web interface presents the data in an intuitive dashboard with:
    - Session lists
    - Calorie calculations
    - Progress charts
    - Detailed hiking statistics

## Project Structure

### Raspberry Pi Components

- raspi/
    - `wserver.py` - Web server and main application entry point
    - `receiver.py` - Standalone Bluetooth receiver
    - `bt.py` - Bluetooth communication module
    - `db.py` - Database interface for storing hiking sessions
    - `hike.py` - Defines the HikeSession class and utility functions

### LilyGo Watch Components

- lilygo/src/
    - `main.cpp` - Main application logic for the watch
    - `config.h` - Hardware configuration and library includes
    - `utils.h/cpp` - File system utility functions
    - `platformio.ini` - PlatformIO project configuration

## Configuration

### Raspberry Pi Configuration

The system uses the following constants which can be modified in their respective files:

- `bt.py`:
    - `WATCH_BT_MAC` - MAC address of the wearable device
    - `WATCH_BT_PORT` - Bluetooth port for communication

- `hike.py`:
    - `MET_HIKING` - MET value for hiking (default: 6)
    - `KCAL_PER_STEP` - Calories burned per step (default: 0.005)

- `db.py`:
    - `DB_FILE_NAME` - SQLite database filename (default: 'sessions.db')

### LilyGo Watch Configuration

Edit the following in the appropriate files:

- `config.h`:
    - Uncomment the appropriate line for your watch model:
        - `LILYGO_WATCH_2020_V2` for T-Watch 2020 V2
        - `LILYGO_WATCH_2020_V3` for T-Watch 2020 V3 (default)

## Troubleshooting

### Bluetooth Connection Issues

If the system fails to connect to the wearable device:

1. Verify the MAC address in `bt.py` matches your device
2. Ensure the wearable device is powered on and in pairing mode
3. Check Bluetooth is enabled on your system

