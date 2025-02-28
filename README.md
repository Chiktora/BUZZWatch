# BUZZWatch - Beehive Monitoring System

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

A comprehensive monitoring system for beehives using Raspberry Pi that tracks temperature, humidity, and weight data with high precision, allowing beekeepers to remotely monitor their hives.

![BUZZWatch System](https://github.com/Chiktora/BUZZWatch/raw/master/Marketing/buzzwatch_header.png)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [HX711 Weight Sensor Calibration](#hx711-weight-sensor-calibration)
- [DHT22 Temperature & Humidity Sensors](#dht22-temperature--humidity-sensors)
- [ThingSpeak Integration](#thingspeak-integration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview
BUZZWatch is a Raspberry Pi-based monitoring system designed for beekeepers who want to collect precise data from their hives. The system collects:
- Indoor temperature and humidity (inside the hive)
- Outdoor temperature and humidity (ambient conditions)
- Hive weight with high-precision calibration
- Uploads all data to ThingSpeak for visualization and analysis

This allows beekeepers to:
- Monitor honey production through weight changes
- Track optimal hive conditions
- Compare indoor/outdoor climate correlations
- Detect potential issues early

## Features
- **Multi-Sensor Integration**:
  - Dual DHT22 temperature and humidity sensors (indoor/outdoor)
  - HX711 high-precision weight sensor with load cells
  - Automatic environmental data collection

- **High-Precision Weight Measurement**:
  - Advanced three-step calibration process
  - Statistical analysis with outlier detection
  - Raw data access for debugging
  - Stability assessment during readings

- **Robust Data Handling**:
  - Automatic sensor error recovery
  - Multi-reading approach for improved accuracy
  - Detailed error logging system
  - Data validation before uploading

- **ThingSpeak Cloud Integration**:
  - Automated data uploads to ThingSpeak
  - Custom field mappings for all sensors
  - Connection testing functionality
  - Error handling for offline operation

- **Comprehensive Testing Suite**:
  - Individual component tests
  - End-to-end system tests
  - Diagnostic tools for troubleshooting
  - Calibration utilities

## Hardware Requirements
- **Raspberry Pi**:
  - Any model with GPIO pins (Raspberry Pi 3B+ or 4 recommended)
  - Stable power supply (2.5A+ recommended)
  - Internet connection (Wi-Fi or Ethernet)

- **Temperature & Humidity Sensors**:
  - 2× DHT22 sensors with connecting wires
  - Indoor sensor connected to GPIO4
  - Outdoor sensor connected to GPIO17
  - 4.7kΩ-10kΩ pull-up resistors (one for each sensor)

- **Weight Sensor**:
  - HX711 load cell amplifier
  - DOUT connected to GPIO27
  - SCK connected to GPIO22
  - Compatible load cells (50kg recommended for beehives)
  - Stable mounting platform

- **Additional Components**:
  - Weatherproof enclosure for outdoor components
  - Appropriate cabling and connectors
  - Mounting hardware for sensors

## Software Requirements
- **Raspberry Pi OS**:
  - Bullseye or newer recommended
  - Python 3.6 or higher

- **Required System Packages**:
  ```bash
  sudo apt-get install -y python3-full python3-pip python3-dev python3-setuptools libgpiod2
  ```

- **Python Dependencies**:
  - `RPi.GPIO`: GPIO control
  - `adafruit-circuitpython-dht`: For DHT22 sensors
  - `requests`: For ThingSpeak API
  - `numpy`: For statistical calculations
  - `typing`: For type hints

## Installation
1. **Prepare the Raspberry Pi**:
   ```bash
   # Update system packages
   sudo apt-get update
   sudo apt-get upgrade

   # Install system dependencies
   sudo apt-get install -y python3-full python3-pip python3-dev python3-setuptools libgpiod2
   ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/Chiktora/BUZZWatch.git
   cd BUZZWatch
   ```

3. **Set Up a Python Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install DHT22 Library**:
   ```bash
   pip install adafruit-circuitpython-dht
   ```

## Configuration
1. **Set Up ThingSpeak**:
   - Create a [ThingSpeak](https://thingspeak.com) account
   - Create a new channel with the following fields:
     - Field 1: Indoor Temperature (°C)
     - Field 2: Indoor Humidity (%)
     - Field 3: Outdoor Temperature (°C)
     - Field 4: Outdoor Humidity (%)
     - Field 5: Weight (kg)
   - Copy your ThingSpeak Write API Key

2. **Configure BUZZWatch**:
   - Copy the example config file:
     ```bash
     cp raspberry_pi_code/config.py.example raspberry_pi_code/config.py
     ```
   - Edit the config file and add your ThingSpeak API Key:
     ```bash
     nano raspberry_pi_code/config.py
     ```
   - Adjust any GPIO pin assignments if your hardware setup differs

3. **Set Up Startup Script**:
   - Copy the example startup script:
     ```bash
     cp start.sh.example start.sh
     ```
   - Make it executable:
     ```bash
     chmod +x start.sh
     ```

## Usage
1. **Start the Monitoring System**:
   ```bash
   ./start.sh
   ```

2. **View Data on ThingSpeak**:
   - Log in to your ThingSpeak account
   - Navigate to your channel
   - View real-time data and visualizations

3. **For Automatic Startup on Boot**:
   ```bash
   # Edit the crontab
   crontab -e
   
   # Add this line (adjust path if needed)
   @reboot cd /home/pi/BUZZWatch && ./start.sh
   ```

## HX711 Weight Sensor Calibration
The system includes a sophisticated calibration system for the HX711 weight sensor to ensure accurate readings.

### Calibration Process
1. **Run the Calibration Wizard**:
   ```bash
   python raspberry_pi_code/tests/test_hx711.py
   ```

2. **Follow the Three-Step Process**:
   - **Empty Scale**: Measures baseline with nothing on the scale
   - **Tare Weight**: Measures with only the platform/board
   - **Reference Weight**: Measures with a known weight on the platform

3. **Advanced Measurement Options**:
   ```bash
   # Take comprehensive measurements with statistics
   python raspberry_pi_code/tests/test_hx711.py --measure

   # Live continuous weight testing
   python raspberry_pi_code/tests/test_hx711.py --test

   # Show calibration information
   python raspberry_pi_code/tests/test_hx711.py --info
   ```

### Calibration Features
- **High-Precision Mode**:
  - Takes 150 measurements per calibration step
  - Advanced outlier detection using IQR method
  - Detailed statistical analysis
  - Confidence interval calculation

- **Comprehensive Statistics**:
  - Mean, median, and range calculations
  - Standard deviation and variance
  - Coefficient of variation for stability assessment
  - 95% confidence intervals

## DHT22 Temperature & Humidity Sensors
The system uses dual DHT22 sensors to monitor both inside the hive and the ambient environment.

### Sensor Testing
```bash
# Test indoor sensor
python raspberry_pi_code/tests/test_dht22_indoor.py

# Test outdoor sensor
python raspberry_pi_code/tests/test_dht22_outdoor.py

# Basic DHT22 test for troubleshooting
python raspberry_pi_code/tests/test_dht22_basic.py
```

### DHT22 Features
- **Robust Reading Mechanism**:
  - Multiple readings with averaging
  - Automatic retry on failed reads
  - Runtime error handling
  - Temperature/humidity validation

- **CircuitPython Implementation**:
  - Modern driver for better stability
  - Proper GPIO cleanup
  - Better platform support
  - Improved error handling

## ThingSpeak Integration
The system automatically sends data to ThingSpeak for visualization and analysis.

### Data Upload Process
- Temperature data in °C with 1 decimal place
- Humidity data in % RH with 1 decimal place
- Weight data in kg with 2 decimal places
- Data uploaded at configurable intervals (default: every minute)

### Testing the Connection
```bash
python raspberry_pi_code/tests/test_thingspeak.py
```

### Visualization Possibilities
- Weight trends over time (daily, weekly, monthly)
- Temperature and humidity correlations
- Weather impact on hive weight
- Custom alerts for abnormal conditions

## Testing
Individual component tests are available in the `tests` directory:

```bash
# All-in-one sensors and connection test
python raspberry_pi_code/tests/test_sensors_and_connection.py

# ThingSpeak connection test
python raspberry_pi_code/tests/test_thingspeak.py

# DHT22 temperature/humidity sensor tests
python raspberry_pi_code/tests/test_dht22_indoor.py
python raspberry_pi_code/tests/test_dht22_outdoor.py

# HX711 weight sensor test
python raspberry_pi_code/tests/test_hx711.py
```

## Troubleshooting

### Common Issues
1. **Sensor Reading Errors**:
   - Check physical connections
   - Verify power supply voltage
   - Ensure pull-up resistors are correctly installed for DHT22
   - Confirm GPIO pins match configuration

2. **Weight Sensor Problems**:
   - Recalibrate using the high-precision mode
   - Check load cell connections
   - Ensure stable mounting platform
   - Verify HX711 power supply

3. **ThingSpeak Connection Issues**:
   - Verify API key is correct
   - Check internet connectivity
   - Ensure field mapping matches ThingSpeak channel
   - Check error logs for specific errors

### Error Logs
- Check the `errors` directory for detailed error logs
- Each error is time-stamped and categorized
- Logs provide specific error messages to aid debugging

## Project Structure
```
BUZZWatch/
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── start.sh                 # Startup script
├── .gitignore               # Git ignore file
├── errors/                  # Error log directory
├── raspberry_pi_code/       # Main codebase
│   ├── __init__.py          # Package indicator
│   ├── config.py            # Configuration file
│   ├── config.py.example    # Example configuration
│   ├── errors.py            # Error handling utilities
│   ├── data_collection_layer/  # Data collection components
│   │   └── data_collector.py   # Main data collection logic
│   ├── hardware_layer/         # Hardware interfaces
│   │   └── sensors.py          # Sensor implementations
│   ├── services/               # External services
│   │   └── api/
│   │       └── thingspeak.py   # ThingSpeak API integration
│   ├── scripts/                # Utility scripts
│   └── tests/                  # Test modules
│       ├── test_dht22_basic.py         # Basic DHT22 test
│       ├── test_dht22_circuitpython.py # CircuitPython DHT test
│       ├── test_dht22_indoor.py        # Indoor DHT22 test
│       ├── test_dht22_outdoor.py       # Outdoor DHT22 test
│       ├── test_hx711.py               # HX711 weight sensor test
│       ├── test_sensors_and_connection.py  # Full system test
│       └── test_thingspeak.py          # ThingSpeak API test
└── venv/                    # Virtual environment (not in repo)
```

## Contributing
Contributions to BUZZWatch are welcome! Here's how to contribute:

1. **Fork the Repository**:
   - Click the "Fork" button at the top-right of the repository page

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/BUZZWatch.git
   ```

3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**:
   - Implement your features or fixes
   - Add tests for new functionality
   - Update documentation as needed

5. **Commit Your Changes**:
   ```bash
   git commit -m "Add some feature"
   ```

6. **Push to Your Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes in detail

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**BUZZWatch** - Making beehive monitoring smart, simple, and precise. 