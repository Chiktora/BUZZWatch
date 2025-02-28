# BUZZWatch - Raspberry Pi Documentation

![Raspberry Pi](https://img.shields.io/badge/device-Raspberry%20Pi-red.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![ThingSpeak](https://img.shields.io/badge/cloud-ThingSpeak-green.svg)

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Hardware Setup](#hardware-setup)
3. [Software Components](#software-components)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [Sensor Operation](#sensor-operation)
7. [Data Flow](#data-flow)
8. [High-Precision Load Cell Calibration](#high-precision-load-cell-calibration)
9. [ThingSpeak Integration](#thingspeak-integration)
10. [Testing and Troubleshooting](#testing-and-troubleshooting)
11. [Error Handling](#error-handling)
12. [Reference](#reference)

## System Architecture

BUZZWatch follows a structured layered architecture that separates responsibilities into distinct components:

```
BUZZWatch/
├── errors/                  # Error log storage
├── venv/                    # Python virtual environment
├── raspberry_pi_code/
│   ├── config.py            # Pin mapping and configuration
│   ├── errors.py            # Error logging functionality
│   ├── hardware_layer/      # Direct hardware interaction
│   │   └── sensors.py       # Sensor initialization and reading
│   ├── data_collection_layer/ # Data processing and aggregation
│   │   └── data_collector.py  # Main data collection logic
│   ├── services/            # External services integration
│   │   └── api/
│   │       └── thingspeak.py # ThingSpeak API communication
│   ├── scripts/             # Entry point scripts
│   │   └── run_pi.py        # Main application runner
│   └── tests/               # Test utilities
│       └── test_*.py        # Individual component tests
├── requirements.txt         # Python dependencies
├── start.sh                 # Startup script
└── README.md                # Project documentation
```

The architecture follows a clear separation of concerns:
- **Hardware Layer**: Manages direct hardware interactions with sensors
- **Data Collection Layer**: Processes and aggregates sensor data
- **Services Layer**: Handles external API integrations (ThingSpeak)
- **Scripts**: Provides entry points and utilities for running the system
- **Configuration**: Centralizes all configurable parameters

## Hardware Setup

### Components Required
- **Raspberry Pi** (any model with GPIO pins)
- **DHT22 Temperature & Humidity Sensors** (2x)
- **HX711 Load Cell Amplifier**
- **Load Cells** (typically 4x for a scale platform)
- **Wooden Platform** (for placing on the load cells)

### Pin Connections
1. **Indoor DHT22 Sensor**:
   - Data pin: GPIO4
   - Power: 3.3V or 5V (check sensor specifications)
   - Ground: GND

2. **Outdoor DHT22 Sensor**:
   - Data pin: GPIO17
   - Power: 3.3V or 5V (check sensor specifications)
   - Ground: GND

3. **HX711 Load Cell Amplifier**:
   - DOUT: GPIO27
   - SCK (PD_SCK): GPIO22
   - Power: 3.3V or 5V (check HX711 specifications)
   - Ground: GND

4. **Load Cells**:
   - Connect to HX711 following the amplifier's documentation
   - Typically wired in a Wheatstone bridge configuration

### Wiring Diagram

```
Raspberry Pi                DHT22 (Indoor)
+--------+                  +--------+
|      3V|------------------|VCC     |
|    GPIO4|-----------------|DATA    |
|     GND|------------------|GND     |
+--------+                  +--------+

Raspberry Pi                DHT22 (Outdoor)
+--------+                  +--------+
|      3V|------------------|VCC     |
|   GPIO17|-----------------|DATA    |
|     GND|------------------|GND     |
+--------+                  +--------+

Raspberry Pi                HX711
+--------+                  +--------+
|      5V|------------------|VCC     |
|   GPIO27|-----------------|DOUT    |
|   GPIO22|-----------------|SCK     |
|     GND|------------------|GND     |
+--------+                  +--------+
                                |
                          Load Cells (4x)
                          +-------------+
```

## Software Components

### 1. Hardware Layer (`sensors.py`)
Responsible for initializing and reading data from physical sensors:
- **DHT22 Sensors**: Measures temperature and humidity
- **HX711 Load Cells**: Measures weight with high precision
- Implements calibration routines for the HX711 sensor
- Handles error conditions and sensor initialization failures

### 2. Data Collection Layer (`data_collector.py`)
Orchestrates the data collection process:
- Initializes with a ThingSpeak API key
- Collects data from all sensors
- Converts weight to kg with 2 decimal places for ThingSpeak
- Uploads all sensor data to ThingSpeak
- Handles errors during the collection process

### 3. Services Layer (`thingspeak.py`)
Manages communication with the ThingSpeak API:
- Tests connection to ThingSpeak
- Uploads sensor data to appropriate fields
- Maps data to ThingSpeak fields (temperature, humidity, weight)
- Handles API errors and connectivity issues

### 4. Error Handling (`errors.py`)
Provides centralized error logging:
- Logs errors to a JSON file with timestamps
- Includes error codes and detailed messages
- Creates the error log directory if it doesn't exist

### 5. Main Application (`run_pi.py`)
The entry point for the application:
- Initializes the data collector
- Tests connection to ThingSpeak
- Runs in a continuous loop, collecting and uploading data
- Handles exceptions and interrupts

## Installation Guide

### Prerequisites
- Raspberry Pi with Raspberry Pi OS (Raspbian) installed
- Python 3.6 or higher installed
- Internet connection for ThingSpeak uploads

### Step 1: Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-full python3-pip python3-dev python3-setuptools libgpiod2
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/Chiktora/BUZZWatch.git
cd BUZZWatch
```

### Step 3: Set Up Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Custom Libraries for Sensors
```bash
# Install DHT22 library
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
python setup.py install
cd ..

# Install HX711 library
git clone https://github.com/tatobari/HX711_Python.git
cd HX711_Python
python setup.py install
cd ..
```

### Step 5: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Configure the System
```bash
# Copy example configuration
cp raspberry_pi_code/config.py.example raspberry_pi_code/config.py

# Edit configuration file with your details
nano raspberry_pi_code/config.py
```

### Step 7: Set Up ThingSpeak
1. Create a ThingSpeak account at https://thingspeak.com
2. Create a new channel with 5 fields:
   - Field 1: Indoor Temperature
   - Field 2: Indoor Humidity
   - Field 3: Outdoor Temperature
   - Field 4: Outdoor Humidity
   - Field 5: Weight
3. Get your Write API Key
4. Update the `THINGSPEAK_API_KEY` in `config.py`

### Step 8: Prepare the Startup Script
```bash
cp start.sh.example start.sh
chmod +x start.sh
```

## Configuration

The system is configured through the `config.py` file, which includes:

### ThingSpeak Configuration
```python
THINGSPEAK_API_KEY = "YOUR_API_KEY_HERE"
```

### Pin Configuration
```python
# Sensor Configuration
INDOOR_DHT22_PIN = 4    # GPIO4
OUTDOOR_DHT22_PIN = 17  # GPIO17
HX711_DOUT_PIN = 27     # GPIO27
HX711_SCK_PIN = 22      # GPIO22
```

### Data Collection Settings
```python
# Data Collection Configuration
COLLECTION_INTERVAL = 60  # seconds
```

## Sensor Operation

### DHT22 Sensors
The system uses the Adafruit CircuitPython DHT library to read temperature and humidity data:
- **Temperature Range**: -40°C to 80°C, ±0.5°C accuracy
- **Humidity Range**: 0-100% RH, ±2-5% accuracy
- Each sensor is read 5 times in succession to ensure reliable data
- Readings are averaged to reduce noise

### HX711 Load Cell System
The weight sensing system uses the HX711 24-bit ADC with load cells:
- **Resolution**: 24-bit
- **Multiple readings**: Each measurement averages multiple samples
- **Advanced Calibration**: Three-step high-precision calibration process
- **Outlier Detection**: IQR-based statistical filtering (1.3×IQR method)
- **Weight Conversion**: Raw values are converted to grams or kg based on calibration

### Key Functions

#### Temperature and Humidity
```python
def read_dht22_indoor():
    """
    Read temperature/humidity from indoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
    
def read_dht22_outdoor():
    """
    Read temperature/humidity from outdoor sensor.
    Returns (temp_c, humidity) or (None, None) on error.
    """
```

#### Weight Measurement
```python
def read_weight(return_kg=True):
    """
    Read weight from HX711 sensor.
    Args:
        return_kg: If True, returns weight in kilograms, otherwise in grams
    Returns:
        Weight value or None on error.
    """
    
def read_weight_for_thingspeak():
    """
    Read weight formatted for ThingSpeak (kg with 2 decimal places).
    Returns:
        Weight in kg or None on error.
    """
```

## Data Flow

1. **Sensor Reading**:
   - DHT22 sensors are read for temperature and humidity
   - HX711 load cells are read for weight data
   
2. **Data Processing**:
   - Temperature and humidity readings are averaged over multiple samples
   - Weight readings are filtered for outliers and averaged
   - Weight is converted to kg with 2 decimal places for ThingSpeak
   
3. **Data Uploading**:
   - All sensor data is packaged for ThingSpeak
   - Data is sent via HTTP POST to ThingSpeak API
   - Response is checked for successful upload
   
4. **Monitoring and Storage**:
   - ThingSpeak stores data for visualization and analysis
   - Local console displays current readings
   - Errors are logged to local error log file

## High-Precision Load Cell Calibration

The system includes an advanced calibration system for the HX711 load cells:

### Three-Step Calibration Process
1. **Empty Scale**: Measures baseline with nothing on the scale
2. **Tare Weight**: Measures with only the wooden platform
3. **Reference Weight**: Measures with a known reference weight on the platform

### Calibration Features
- **High Sample Count**: Takes 150 measurements per calibration step
- **Statistical Analysis**: Computes mean, median, standard deviation, CV%
- **Outlier Removal**: Uses 1.3×IQR method to filter anomalous readings
- **Confidence Intervals**: Calculates 95% confidence intervals
- **Progress Tracking**: Batch-based progress indicators

### Running Calibration
```bash
python raspberry_pi_code/tests/test_hx711.py
```

This starts the interactive calibration wizard which will guide you through the process:

1. Remove all weight from the scale
2. Place only the wooden platform on the scale
3. Place your reference weight (e.g., 1kg) on the platform
4. Enter the exact reference weight value when prompted
5. Wait for the calibration process to complete
6. Test the calibration accuracy

### Calibration Storage
- Calibration data is stored in JSON format
- File location: `BUZZWatch/raspberry_pi_code/config/hx711_calibration.json`
- Includes detailed metadata for reference:
  - Calibration date and time
  - Reference weight used
  - Raw values for each step
  - Statistical measures of stability

Sample calibration file:
```json
{
    "reference_unit": 2.248711,
    "zero_offset": -116261.13,
    "calibration_date": "2023-02-28 18:45:22",
    "known_weight_used": 1000.0,
    "empty_raw": -118263.45,
    "tare_raw": -116261.13,
    "weight_raw": -114012.42,
    "sensitivity": 2.248711,
    "tare_weight_raw_difference": 2002.32,
    "three_step_calibration": true,
    "measurements_per_step": 150,
    "empty_cv": 3.21,
    "tare_cv": 2.65,
    "weight_cv": 5.47,
    "calibration_precision": "high"
}
```

### Calibration Testing
The system tests calibration quality after completion:
- Tests with board only (should read near zero)
- Tests with reference weight (should match known weight)
- Calculates error percentage and provides quality rating

## ThingSpeak Integration

ThingSpeak provides cloud storage and visualization for the sensor data:

### Data Structure
- **Field 1**: Indoor Temperature (°C with 1 decimal place)
- **Field 2**: Indoor Humidity (% RH with 1 decimal place)
- **Field 3**: Outdoor Temperature (°C with 1 decimal place)
- **Field 4**: Outdoor Humidity (% RH with 1 decimal place)
- **Field 5**: Weight (kg with 2 decimal places)

### Upload Process
1. Data is collected from sensors
2. Weight is converted to kg with exactly 2 decimal places
3. All data is uploaded to ThingSpeak once per minute
4. Failed uploads are logged and retried in the next cycle

### API Communication
- Uses HTTPS POST requests to the ThingSpeak API
- Requires a valid API Write Key
- Tests connection at startup
- Handles connection failures gracefully

### Example Data
```
Indoor: 24.5°C, 45.2% RH
Outdoor: 18.3°C, 62.7% RH
Weight: 42.55 kg
```

### Visualization
On ThingSpeak, you can create:
- Time-series graphs of all variables
- Comparative charts (indoor vs. outdoor temperature)
- Weight trend analysis
- Custom calculations and alerts

## Testing and Troubleshooting

The system includes comprehensive test utilities:

### Component Tests
```bash
# Test ThingSpeak connection
python raspberry_pi_code/tests/test_thingspeak.py

# Test indoor DHT22
python raspberry_pi_code/tests/test_dht22_indoor.py

# Test outdoor DHT22
python raspberry_pi_code/tests/test_dht22_outdoor.py

# Test HX711 weight sensor
python raspberry_pi_code/tests/test_hx711.py
```

### HX711 Testing Options
```bash
# Run the calibration wizard
python raspberry_pi_code/tests/test_hx711.py

# Comprehensive measurement mode
python raspberry_pi_code/tests/test_hx711.py --measure

# Live weight testing
python raspberry_pi_code/tests/test_hx711.py --test

# View calibration information
python raspberry_pi_code/tests/test_hx711.py --info
```

### Common Issues and Solutions

1. **DHT22 Reading Failures**
   - **Symptoms**: Missing temperature or humidity data
   - **Causes**: Wiring issues, power issues, interference
   - **Solution**: Check wiring, ensure stable power, try moving sensor away from interference sources

2. **HX711 Reading Issues**
   - **Symptoms**: Unstable weight readings, timeout errors
   - **Causes**: Poor calibration, loose connections, environmental factors
   - **Solution**: Recalibrate using the high-precision mode, check wiring, ensure stable platform

3. **ThingSpeak Connection Failures**
   - **Symptoms**: Upload failure messages, missing data points
   - **Causes**: Internet connectivity issues, API key problems
   - **Solution**: Check internet connection, verify API key is correct

4. **Calibration Issues**
   - **Symptoms**: Inconsistent weight readings, high error percentages
   - **Causes**: Unstable platform, vibrations, air currents, temperature changes
   - **Solution**: 
     - Ensure the scale is on a stable, level surface
     - Keep away from air vents or open windows
     - Place the load cells on a rigid, non-flexible surface
     - Center the platform and weights carefully

## Error Handling

The system uses a structured error logging system:

### Error Logging
- Errors are logged to `errors/errors.json`
- Each error includes:
  - Error code (e.g., "ERR_DHT22_INIT")
  - Detailed error message
  - Timestamp

### Common Error Codes
- **ERR_DHT22_INIT**: Error initializing DHT22 sensors
- **ERR_DHT22_INDOOR**: Error reading from indoor DHT22
- **ERR_DHT22_OUTDOOR**: Error reading from outdoor DHT22
- **ERR_HX711_INIT**: Error initializing HX711 sensor
- **ERR_HX711_CALIBRATION**: Error during calibration process
- **ERR_WEIGHT**: Error reading weight from HX711
- **ERR_THINGSPEAK_TEST**: Error testing ThingSpeak connection
- **ERR_THINGSPEAK_UPLOAD**: Error uploading data to ThingSpeak
- **ERR_DATA_COLLECTION**: Error in the data collection process
- **ERR_MAIN**: General error in the main application

Sample error log entry:
```json
{
    "code": "ERR_HX711_CALIBRATION",
    "message": "Reading from HX711 timed out after 3 seconds",
    "timestamp": "2023-02-28 17:42:15"
}
```

## Reference

### Key Python Libraries
- **RPi.GPIO**: Controls GPIO pins on Raspberry Pi
- **adafruit-circuitpython-dht**: Reads DHT22 sensors
- **hx711**: Interfaces with HX711 load cell amplifier
- **requests**: Handles HTTP communications with ThingSpeak
- **numpy**: Provides advanced statistical functions for analysis

### File Locations
- **Configuration**: `raspberry_pi_code/config.py`
- **Calibration Data**: `raspberry_pi_code/config/hx711_calibration.json`
- **Error Logs**: `errors/errors.json`
- **Main Script**: `raspberry_pi_code/scripts/run_pi.py`

### Execution
To start the BUZZWatch system:
```bash
./start.sh
```

This will run the system in the foreground. For production deployment, consider using a service manager like systemd to keep the application running continuously and to restart it automatically if it crashes.

### Setting Up as a Service
To set up BUZZWatch as a systemd service:

1. Create a service file:
```bash
sudo nano /etc/systemd/system/buzzwatch.service
```

2. Add the following content:
```
[Unit]
Description=BUZZWatch Beehive Monitoring System
After=network.target

[Service]
ExecStart=/home/pi/BUZZWatch/start.sh
WorkingDirectory=/home/pi/BUZZWatch
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable buzzwatch.service
sudo systemctl start buzzwatch.service
```

4. Check status:
```bash
sudo systemctl status buzzwatch.service
```

### Maintenance Tasks

#### Periodic Calibration
It's recommended to recalibrate the load cells:
- At least once per month
- Any time the scale is moved
- If temperature conditions change significantly
- If readings begin to drift or show inconsistency

#### System Updates
To update the BUZZWatch system:
```bash
cd /home/pi/BUZZWatch
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart buzzwatch.service
```

#### Backing Up Calibration Data
Periodically back up your calibration file:
```bash
cp /home/pi/BUZZWatch/raspberry_pi_code/config/hx711_calibration.json /home/pi/hx711_calibration_backup_$(date +%Y%m%d).json
```

---

**Created:** March 2023  
**Last Updated:** May 2023

For more information, visit [GitHub repository](https://github.com/Chiktora/BUZZWatch) 