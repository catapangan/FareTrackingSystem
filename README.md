# FareTrackingSystem
Python-based Fare Tracking System using Serila GPS and USB keyboard-input RFID Reader

Software Requirements:
- Raspbian buster
- Driver installation for TFT Screen (https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install-2)
- Python version >= 3.7
- PostgreSQL
- NGINX
- PHP

Hardware Requirements:
- Raspberry Pi 3 Model B+
- Adafruit 240x320 TFT Screen
- Serial GPS Sensor with GPGLL
- Keyboard-input RFID Reader

Python Dependencies:
- psycopg2
- haversine
- numpy
- folium
- pyqt5
- pyqt5 webkit
- pynput

Setting up the scripts:
1. Clone repository
2. Add downloaded offline tile maps to ./data/tiles/
3. Direct nginx root to ./html/ or copy contents of ./html to nginx root directory (e.g. /var/www/html/)
4. Add execution for gps_logger.py and user_logger.py to Raspberry Pi LXDE autostart (e.g. ~/.config/lxsession/LXDE-pi/autostart)
5. Reboot
