# BUZZWatch Project for Raspberry Pi

A monitoring system for beehives using Raspberry Pi that collects temperature, humidity, and weight data.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

## Overview
BUZZWatch is a Raspberry Pi-based monitoring system for beehives that collects:
- Indoor temperature and humidity (inside the hive)
- Outdoor temperature and humidity (ambient conditions)
- Hive weight
- Uploads data to ThingSpeak for visualization and analysis

## Hardware Requirements
- Raspberry Pi (any model with GPIO pins)
- 2x DHT22 Temperature & Humidity Sensors
  - Indoor sensor connected to GPIO4
  - Outdoor sensor connected to GPIO17
- HX711 Weight Sensor
  - DOUT connected to GPIO5
  - SCK connected to GPIO6

## Software Requirements
- Python 3.6 or higher
- Required Python packages (listed in requirements.txt):
  - Adafruit-Blinka
  - adafruit-circuitpython-dht
  - hx711
  - requests

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
     - Field 5: Weight
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
   - Upload data to ThingSpeak every minute
   - Display current readings in the console
   - Log any errors to the errors directory

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

## Troubleshooting
- Check the errors directory for detailed error logs
- Ensure all sensors are properly connected
- Verify your ThingSpeak API key is correct
- Make sure you have internet connectivity

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
