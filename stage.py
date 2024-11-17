## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage
import serial
import time
import threading

BASEVELOCITY = 10    #mm/s
MAXVELOCITY = 25    ##mm/s
STEPSTODISTANCE = 0.025 #mm/step
STAGELENGTH = 500   ##mm

## It is COM7 on my laptop, might be different on other devices
bluetooth_serial = serial.Serial("COM7", 921600)

class stage:
    '''Stage Object: Controls position of the stage, and deals with calibration'''
    def __init__(self):
        listener_thread = threading.Thread(target=self.listen_for_limit_switch, daemon=True)
        listener_thread.start()
        self.position = 0
        self.calibrate()

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## Attempts to move the stage backwards the distance of the stage so it will reach the limit switch
        print("Calibrating")
        dist = STAGELENGTH
        direction = False
        stepFrequency, numSteps = self.getStepFrequencyAndNumSteps(dist)
        self.sendMoveCommand(stepFrequency, numSteps, direction)

    def moveto(self, position, velocity = BASEVELOCITY):
        '''Moves the linear stage to a position'''
        if (position > 0 and position < STAGELENGTH) and (velocity > 0 and velocity < MAXVELOCITY):
            ## Find Distance to travel
            dist = abs(self.position - position)
            ## Find direction to travel. Away from home is True, towards home is False (Need decide which side is home so this could change)
            direction = True if self.position < position else False
            # direction = False ## Towards end without motor
            # direction = True ## Towards end with motor
            ## Convert distance and velocity to frequency of steps, and number of steps
            stepFrequency, numSteps = self.getStepFrequencyAndNumSteps(dist)
            self.sendMoveCommand(stepFrequency, numSteps, direction)
            print("Move stage to ", position, "with velocity ", velocity)
            print("Distance: ", dist, " Frequency: ", stepFrequency, " Steps: ", numSteps, " Direction: ", direction)
        else:
            print("Position or velocity are out of range")

    def getStepFrequencyAndNumSteps(self, distance, velocity=BASEVELOCITY):
        numSteps = distance/STEPSTODISTANCE
        stepFrequency = velocity/STEPSTODISTANCE
        return stepFrequency, numSteps

    def sendMoveCommand(self, stepFrequency, numSteps, direction):
        command = f"{stepFrequency},{numSteps},{int(direction)}\n"
        bluetooth_serial.write(command.encode())
        print("Sent command:", command)
        time.sleep(0.1)

    def listen_for_limit_switch(self):
        '''Function to listen for messages from ESP32 in a seperate thread'''
        while True:
            if bluetooth_serial.in_waiting > 0:
                message = bluetooth_serial.readline().decode().strip()
                if message == "LIMIT_SWITCH_TRIGGERED":
                    self.position = 0
                    print("Limit switch was triggered, stage is at home position")
                else:
                    print("Received message:", message)
            time.sleep(0.1)
    
if __name__ == '__main__':
    stage = stage()
    time.sleep(30)
    stage.moveto(200)
    time.sleep(60)