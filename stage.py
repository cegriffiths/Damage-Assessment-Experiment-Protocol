## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage
import serial
import time
import threading
import os

BASEVELOCITY = 10    #mm/s
MAXVELOCITY = 25    ##mm/s
STEPSTODISTANCE = 0.025 #mm/step
STAGELENGTH = 450   ##mm

## It is COM7 on my laptop, might be different on other devices
bluetooth_serial = serial.Serial("COM7", 921600)

class stage:
    '''Stage Object: Controls position of the stage, and deals with calibration'''
    def __init__(self):
        listener_thread = threading.Thread(target=self.listen_for_limit_switch, daemon=True)
        listener_thread.start()
        self.position = 0
        self.motionFlag = False
        self.manualStopFlag = False
        self.calibrate()

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## Attempts to move the stage backwards the distance of the stage so it will reach the limit switch
        print("Calibrating")
        dist = STAGELENGTH
        direction = False
        stepFrequency, numSteps = self.getStepFrequencyAndNumSteps(dist)
        self.sendMoveCommand(stepFrequency, numSteps, direction)
        self.motionFlag = True
        self.waitForStage()
        print("Calibration Complete\n")

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
            ## Set new position
            self.position = self.position + dist if direction else self.position - dist
            ## Set motion flag to true and then wait for stage to stop
            print("Moving Stage")
            self.motionFlag = True
            self.waitForStage()
            print("Moved stage to ", self.position, "with velocity ", velocity, "\n")
            # print("Distance: ", dist, " Frequency: ", stepFrequency, " Steps: ", numSteps, " Direction: ", direction)
        else:
            print("Position or velocity are out of range")

    def waitForStage(self):
        '''Waits for the stage to finish moving'''
        while self.motionFlag:
            time.sleep(1)
            print("waiting")

    def getStepFrequencyAndNumSteps(self, distance, velocity=BASEVELOCITY):
        numSteps = distance/STEPSTODISTANCE
        stepFrequency = velocity/STEPSTODISTANCE
        return stepFrequency, numSteps

    def sendMoveCommand(self, stepFrequency, numSteps, direction):
        command = f"{stepFrequency},{numSteps},{int(direction)}\n"
        bluetooth_serial.write(command.encode())
        print(F"Sent command:{stepFrequency},{numSteps},{int(direction)}")
        time.sleep(0.1)

    def listen_for_limit_switch(self):
        '''Function to listen for messages from ESP32 in a seperate thread'''
        while True:
            if bluetooth_serial.in_waiting > 0:
                message = bluetooth_serial.readline().decode().strip()
                if message == "LIMIT_STOP":
                    self.position = 0
                    self.motionFlag = False
                    print("Stage Home")
                elif message == "MANUAL_STOP":
                    self.motionFlag = False
                    self.manualStopFlag = True
                    print("Manual Stop")
                    os._exit(0)
                elif message == "DONE_MOTION":
                    self.motionFlag = False
                    print("Stage is in place")
                else:
                    print("Received message:", message)
            time.sleep(0.1)
    
if __name__ == '__main__':
    stage = stage()
    stage.moveto(200)
    stage.moveto(10)
    stage.calibrate()
    stage.moveto(20)
    stage.moveto(10)