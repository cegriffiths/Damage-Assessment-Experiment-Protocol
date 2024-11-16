## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage

class stage:
    '''Stage Object: Controls position of the stage, and deals with calibrration'''
    def __init__(self):
        self.pos

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## TODO

    def movedist(self, dist):
        '''Moves the linear stage a distance dist'''
        ## TODO

    def moveto(self, finalpos):
        '''Moves the linear stage to finalpos'''
        ## TODO
        print("Move stage to ", finalpos)


# Temporary to test the esp32 bluetooth
import serial
import time

bluetooth_serial = serial.Serial("COM7", 921600)

def send_command(frequency, steps, direction):
    command = f"{frequency},{steps},{int(direction)}\n"
    bluetooth_serial.write(command.encode())
    print("Sent command:", command)
    time.sleep(0.1)


send_command(300, 1000, True)