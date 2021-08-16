# Content
Brief descrption of files contained in src directory.
## boot_py_scripts.sh
This bash file is intended to run on boot and initialize the gpsd client and start each python script running in the background with their respective virtual environments. This file is set up to run on boot with crontab. There is currently an issue where line-2 requires sudo permissions, but when run on root's crontab - `sudo crontab -e` - the initialization fails. In the debugging process I found that trying to initialize the gpsd client as root also failed, but running as the main user with sudo permissions does work.  currently main.py has the GPS collection disabled. 
## main.py
this is the script that collects Temp, Acceleration, and GPS data from the MPU6050 and GPS module respectively.
## pico subdirectory
This contains the python files associated with logging data from the CANPico.
