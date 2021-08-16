# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import gpiozero
import csv
import smbus
import numpy as np
import spidev
import datetime
import time
import gpsd
import serial
import os
from gps import *
from gpiozero import Button

# MPU Parameters:
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
TEMP_OUT_H = 0x41

# Script Parameters:
SAMPLE_INTERVAL = 1
SAVEPOINT = 10


def MPU_Init():
    # write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)


def n_burst(n, dur: float, LEDname):
    interval = 0.5 * dur / n
    for i in range(0, n):
        time.sleep(interval)
        LEDname.on()
        time.sleep(interval)
        LEDname.off()


def read_raw_data(addr):
    # Values are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if (value > 32768):
        value = value - 65536
    return value


def add_data(A: list):
    temperature = read_raw_data(TEMP_OUT_H)
    temperature = (temperature / 340.0) + 36.53
    # temp_F = (temperature * 1.8) + 32
    # print(temperature)
    # print(temp_F)
    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    # Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0
    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0

    #Get GPS Data
    packet = gpsd.get_current()
    if packet.mode >= 2:
        lat = packet.lat
        lon = packet.lon
    else:
        lat = 'NA'
        lon = 'NA'
    if packet.mode >=3 :
        alt = packet.alt
    else:
        alt = 'NA'
    
    # t = seconds since Unix Epoch (Jan 1st 1970 UTC)
    t = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).timestamp()
    # A = timestamp, temperature, lat, lon, altitude, Accelx, Accely, Accelz, Gyrox, Gyroy, Gyroz, CANvelocity, CANbattSOC, CANbattAmp, CANbattVolt
    A.append([t, temperature, lat, lon, alt, Ax, Ay, Az, Gx, Gy, Gz])
    #print(A[len(A) - 1])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    red = gpiozero.LED(16)
    green = gpiozero.LED(12)
    toggle_switch = Button(26)
    n_burst(200, 30, red)
    
    gpsd.connect()
    #packet = gpsd.get_current()
    n_burst(10, 1, green)
    #print(packet.position())
    #lat = packet.lat
    #lon = packet.lon
    #alt = packet.alt
    #print(lat, lon, alt)

    bus = smbus.SMBus(1)
    Device_Address = 0x68
    MPU_Init()

    #File name is in format: "YYYY-MM-DD (HH-MM-SS).csv"
    start_time = datetime.datetime.utcnow()
    filename_time = start_time.strftime('%Y-%m-%d (%H-%M-%S)')

    #Initialize the file and set a header
    with open(filename_time + '.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['timestamp', 'temperature', 'lat', 'lon', 'altitude', 'Accelx', 'Accely', 'Accelz', 'Gyrox', 'Gyroy',
             'Gyroz'])
    n_burst(3, 1, green)

    A = []
    while True:
        add_data(A)
        red.on()
        time.sleep(SAMPLE_INTERVAL / 2.0)
        red.off()
        time.sleep(SAMPLE_INTERVAL / 2.0)
        # if stop then break
        if len(A) == SAVEPOINT:
            with open(filename_time + '.csv', mode='a') as file:
                writer = csv.writer(file)
                writer.writerows(A)
            A.clear()
            if toggle_switch.is_pressed:
                #print("program ended")
                break
