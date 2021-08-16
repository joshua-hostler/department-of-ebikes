#!/bin/bash
systemctl disable gpsd.socket
gpsd /dev/serial0 -F /var/run/gpsd.sock
/home/pi/Documents/ebikes/data-logger/bin/python3.9 /home/pi/Documents/ebikes/source/main.py &
/home/pi/Documents/ebikes/pico/bin/python3.9 /home/pi/Documents/ebikes/pico/main.py &
