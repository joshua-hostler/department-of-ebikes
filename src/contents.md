#Content
Brief descrption of files contained in src directory.
## boot_py_scripts.sh
This bash file is intended to run on boot and initialize the gpsd client and start each python script running in the background with their respective virtual environments.
## main.py
this is the script that collects Temp, Acceleration, and GPS data from the MPU6050 and GPS module respectively.
## pico subdirectory
This contains the python files associated with logging data from the CANPico.
