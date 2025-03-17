## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage
import serial
import time
import threading
import os
import sys
from PySide6.QtCore import Signal, QObject

BASEVELOCITY = 30    #mm/s
CALIBRATIONVELOCITY = 20 #mm/s
BASEACCELERATION = 50   #mm/s^2
MAXVELOCITY = 50    ##mm/s
STEPSTODISTANCE = 0.025 #mm/step
STAGELENGTH = 451   ##mm


class stage(QObject):
    '''Stage Object: Controls position of the stage, and deals with calibration'''

    shutdown_signal = Signal()
    stage_changed = Signal()


    def __init__(self):
        super().__init__()
        #ESP32 Connection over USB on windows
        # self.esp32serial = serial.Serial('COM5', 921600)
        #ESP32 Connection over USB on Linux
        self.esp32serial = serial.Serial('/dev/ttyUSB0', 921600)


        listener_thread = threading.Thread(target=self.listen_for_limit_switch, daemon=True)
        listener_thread.start()
        
        self._position = 0
        self._motionFlag = False
        self._manualStopFlag = False
        self._state = "Unknown"
        self._previousMotionWasCalibration = False

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## Attempts to move the stage backwards the distance of the stage so it will reach the limit switch
        # print("STAGE: Calibrating")
        dist = STAGELENGTH
        direction = False
        self.sendMoveCommand(direction, dist, CALIBRATIONVELOCITY)
        self.motionFlag = True
        self.waitForStage()
        # self.position = 0
        self._previousMotionWasCalibration = True
        print("STAGE: Calibration Complete")

    def moveto(self, position, velocity = BASEVELOCITY):
        '''Moves the linear stage to a position'''
        if position == self._position:
            print(f"STAGE: Already in position {self._position}")        
        elif (position > 0 and position < STAGELENGTH) and (velocity > 0 and velocity < MAXVELOCITY):
            print(f"STAGE: Moving Stage to {position} with velocity {velocity}")
            ## Find Distance to travel
            dist = abs(self._position - position)
            ## Find direction to travel. Away from home is True, towards home is False (Need decide which side is home so this could change)
            direction = True if self._position < position else False
            # direction = False ## Towards end without motor
            # direction = True ## Towards end with motor
            self.sendMoveCommand(direction, dist)
            ## Set motion flag to true and then wait for stage to stop
            # print("STAGE: Moving Stage")
            self.motionFlag = True
            self.waitForStage()
            ## Set new position
            if (self._position == 0) and (self._previousMotionWasCalibration == False):
                print(f"STAGE: Unexpected limit switch while moving towards home. Calibrate then go to desired position")
                sys.exit()
                # time.sleep(2)
                # self.calibrate()
                # print(f"STAGE: Calibrated after unexpected limit switch")
                # self.moveto(position, velocity)
                # print(f"STAGE: Moved to desired location after unexpected limit switch")
            else:
                self.position = self._position + dist if direction else self._position - dist
                print(f"STAGE: Moved to {self._position} with velocity {velocity}")
                self._previousMotionWasCalibration = False
                # print("Distance: ", dist, " Frequency: ", stepFrequency, " Steps: ", numSteps, " Direction: ", direction)
        else:
            print("STAGE: Position or velocity are out of range")

    def waitForStage(self):
        '''Waits for the stage to finish moving'''
        while self._motionFlag:
            time.sleep(0.1)
            # print("STAGE: moving")

    def sendMoveCommand(self, direction, distance, velocity=BASEVELOCITY, acceleration=BASEACCELERATION):
        # print("STAGE: Sending Command")
        command = f"{distance},{velocity},{acceleration},{int(direction)}\n"
        self.esp32serial.write(command.encode())
        print(F"STAGE: Sent command:{distance},{velocity},{acceleration},{int(direction)}")

    def listen_for_limit_switch(self):
        '''Function to listen for messages from ESP32 in a seperate thread'''
        time.sleep(0.5)
        while True:
            if self.esp32serial.in_waiting > 0:  
                message = self.esp32serial.readline().decode().strip()
                if message == "LIMIT_STOP":
                    self.position = 0
                    self.motionFlag = False
                    print("STAGE: Home")
                elif message == "MANUAL_STOP":
                    self.motionFlag = False
                    self.manualStopFlag = True
                    print("STAGE: Manual Stop")
                elif message == "DONE_MOTION":
                    self.motionFlag = False
                    print("STAGE: In place")
                else:
                    print("STAGE: Received message:" + message)
            time.sleep(0.1)

    def calculate_state(self):
        if self._motionFlag == True and self._manualStopFlag == False:
            self.state = "Moving"
        elif self.motionFlag == False and self._manualStopFlag == True:
            self.state = "Manual Stop"
            self.shutdown_signal.emit()
        elif self._motionFlag == False and self._manualStopFlag == False:
            self.state = "In Position"
        else:
            self.state = "Unknown"
        
        # print("STAGE: State updated: " + self._state)

    @property
    def motionFlag(self):
        return self._motionFlag
    
    @motionFlag.setter
    def motionFlag(self, value):
        self._motionFlag = value
        self.calculate_state()

    @property
    def manualStopFlag(self):
        return self._manualStopFlag
    
    @manualStopFlag.setter
    def manualStopFlag(self, value):
        self._manualStopFlag = value
        self.calculate_state()
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.stage_changed.emit()
    
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        self._position = value
        self.stage_changed.emit()
        # print(f"Position: {self._position}")



if __name__ == '__main__':
    stage = stage()
    stage.calibrate()
    # stage.moveto(74)
    # time.sleep(0.1)
    # stage.moveto(57)
    # time.sleep(0.1)
    # stage.moveto(40)
    # time.sleep(0.1)
    # stage.moveto(23)

    stage.moveto(100)
    time.sleep(0.1)
    stage.moveto(40)
    time.sleep(0.1)
    stage.moveto(23)