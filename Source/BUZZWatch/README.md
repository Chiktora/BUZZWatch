# BUZZWatch Project for Raspberry Pi

A monitoring system for beehives using Raspberry Pi that collects temperature, humidity, and weight data.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

## Overview
BUZZWatch is a Raspberry Pi-based monitoring system for beehives that collects:
- Indoor temperature and humidity (inside the hive)
- Outdoor temperature and humidity (ambient conditions)
- Hive weight with high-precision calibration
- Uploads data to ThingSpeak for visualization and analysis

## Hardware Requirements
- Raspberry Pi (any model with GPIO pins)
- 2x DHT22 Temperature & Humidity Sensors
  - Indoor sensor connected to GPIO4
  - Outdoor sensor connected to GPIO17
- HX711 Weight Sensor with load cells
  - DOUT connected to GPIO5
  - SCK connected to GPIO6
  - Compatible with most load cell configurations

## Software Requirements
- Python 3.6 or higher
- Required Python packages (listed in requirements.txt):
  - Adafruit-Blinka
  - adafruit-circuitpython-dht
  - hx711
  - requests
  - numpy

## Installation
1. Clone this repository:
```bash
git clone https://github.com/Chiktora/BUZZWatch.git
cd BUZZWatch
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up ThingSpeak:
   - Create a ThingSpeak account at https://thingspeak.com
   - Create a new channel with the following fields:
     - Field 1: Indoor Temperature
     - Field 2: Indoor Humidity
     - Field 3: Outdoor Temperature
     - Field 4: Outdoor Humidity
     - Field 5: Weight (in kg with 2 decimal places)
   - Copy your Write API Key

4. Configure the API key:
   - Copy the example startup script:
   ```bash
   cp start.sh.example start.sh
   ```
   - Edit start.sh and add your ThingSpeak Write API Key
   - Make the script executable:
   ```bash
   chmod +x start.sh
   ```

## Usage
1. Start the monitoring system:
```bash
./start.sh
```

2. The system will:
   - Collect data from all sensors every minute
   - Upload data to ThingSpeak every minute (weight in kg with 2 decimal places)
   - Display current readings in the console
   - Log any errors to the errors directory

## HX711 Weight Sensor Calibration
The system includes a high-precision calibration tool for the HX711 weight sensor:

### Calibration Features
- **Three-Step Calibration Process**:
  1. Empty scale measurement (baseline)
  2. Tare measurement (platform/board only)
  3. Known reference weight (on platform)
- **High-Precision Mode**:
  - Takes 150 measurements per calibration step
  - Advanced outlier detection and filtering
  - Comprehensive statistical analysis
  - Confidence interval calculation
- **Real-time Progress Tracking**:
  - Batch progress indicators
  - Stability assessment during calibration
  - Time estimates for each calibration step

### Calibration Instructions
1. Run the calibration wizard:
```bash
python raspberry_pi_code/tests/test_hx711.py
```

2. Follow the on-screen instructions:
   - Start with an empty scale
   - Add the platform/board for tare measurement
   - Add a known reference weight (e.g., 1kg) on top of the platform
   - The tool will calculate precise calibration factors

### Additional Measurement Tools
Several options are available for testing and using the weight sensor:

```bash
# Run the calibration wizard (default)
python raspberry_pi_code/tests/test_hx711.py

# Take comprehensive measurements with statistics
python raspberry_pi_code/tests/test_hx711.py --measure

# Live continuous weight testing
python raspberry_pi_code/tests/test_hx711.py --test

# Show calibration information
python raspberry_pi_code/tests/test_hx711.py --info
```

## Testing
Individual component tests are available in the `tests` directory:
```bash
# Test ThingSpeak connection
python raspberry_pi_code/tests/test_thingspeak.py

# Test indoor DHT22
python raspberry_pi_code/tests/test_dht22_indoor.py

# Test outdoor DHT22
python raspberry_pi_code/tests/test_dht22_outdoor.py

# Test weight sensor
python raspberry_pi_code/tests/test_hx711.py
```

## ThingSpeak Integration
The system automatically sends data to ThingSpeak with the following specifications:
- Temperature data in °C with 1 decimal place
- Humidity data in % RH with 1 decimal place
- Weight data in kg with 2 decimal places
- Data is uploaded every minute

You can create custom charts and widgets on your ThingSpeak channel to visualize:
- Weight trends over time (daily, weekly, monthly)
- Temperature and humidity correlations
- Weather impact on hive weight

## Troubleshooting
- Check the errors directory for detailed error logs
- Ensure all sensors are properly connected
- Verify your ThingSpeak API key is correct
- Make sure you have internet connectivity
- For weight issues, try recalibrating using the high-precision mode

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
