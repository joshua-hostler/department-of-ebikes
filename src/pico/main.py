# this program collects the raw MIN Frames which contain the CANFrames in bytes as the payload.
import logging
import struct
from struct import unpack
from time import sleep, time
import sys
import getopt
from min import MINTransportSerial
from binascii import hexlify
import datetime
import csv
from gpiozero import Button

# Linux USB serial ports are of the form '/dev/ttyACM*' and the CANPico board
# from Canis Labs runs two serial ports, one for the REPL console and one
# for applications to use; the default CANPico firmware includes MIN support
# on this second port
MIN_PORT = '/dev/ttyACM1'


def wait_for_frames(min_handler: MINTransportSerial):
    while True:
        # The polling will generally block waiting for characters on a timeout
        # How much CPU time this takes depends on the Python serial implementation
        # on the target machine
        frames = min_handler.poll()
        if frames:
            return frames


if __name__ == "__main__":
    options = "hp:"

    port = MIN_PORT
    sleep(30)
    try:
        args, vals = getopt.getopt(sys.argv[1:], options)
        for arg, val in args:
            if arg in ("-h"):
                print ("-p [port]")
                quit()
            elif arg in ("-p"):
                port = val
                print("port={}".format(port))

    except getopt.error as err:
        print (str(err))
        quit()

    logging.basicConfig(level=logging.WARNING)

    min_handler = MINTransportSerial(port=port)
    logging.debug("Polling for MIN frames")

    min_handler.transport_reset()
    
    #File name is in format: "YYYY-MM-DD (HH-MM-SS).csv"
    start_time = datetime.datetime.utcnow()
    filename_time = start_time.strftime('%Y-%m-%d (%H-%M-%S)')
    toggle_switch = Button(26)
    
    #Initialize the file and set a header
    with open(filename_time + '.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['canframes'])

    while True:
        if toggle_switch.is_pressed:
            break
        # Wait for one or more frames to come back from the serial line and print them out
        for frame in wait_for_frames(min_handler):
            if frame.min_id == 1:
                with open(filename_time + '.csv', mode='a') as file:
                    writer = csv.writer(file)
                    writer.writerow(frame.payload.hex())

