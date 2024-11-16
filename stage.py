## STAGE SCRIPT
## Author: Chris Griffiths
# Date: October 24, 2024
# UBC ENPH 479

## This script controls the stage
import serial
import time
import threading

BASEVELOCITY = 1    #mm/s
STEPSTODISTANCE = 0.025 #mm/step
STAGELENGTH = 500   ##mm

## It is COM7 on my laptop, might be different on other devices
bluetooth_serial = serial.Serial("COM7", 921600)

class stage:
    '''Stage Object: Controls position of the stage, and deals with calibration'''
    def __init__(self):
        ## One step is 0.025mm
        self.limitSwitchPressed = False

        listener_thread = threading.Thread(target=self.listen_for_limit_switch, daemon=True)
        listener_thread.start()
        self.calibrate()

    def calibrate(self):
        '''Calibrates the linear stage'''
        ## Attempts to move the stage backwards the distance of the stage so it will reach the limit switch
        # command = f"{frequency},{steps},{int(direction)}\n"
        # bluetooth_serial.write(command.encode())
        # print("Sent command:", command)
        # time.sleep(0.1)

    def moveto(self, position, velocity = BASEVELOCITY):
        '''Moves the linear stage to a position'''
        print("Move stage to ", position, "with velocity ", velocity)
        dist = self.position - position

    def listen_for_limit_switch(self):
        '''Function to listen for messages from ESP32 in a seperate thread'''
        while True:
            if bluetooth_serial.in_waiting > 0:
                message = bluetooth_serial.readline().decode().strip()
                if message == "LIMIT_SWITCH_TRIGGERED":
                    command = f"STOP\n"
                    bluetooth_serial.write(command.encode())
                    print("Limit switch was triggered")
                    self.position = 0
                else:
                    print("Received message:", message)
            time.sleep(0.1)
    


# # Temporary to test the esp32 bluetooth
# import serial
# import time

# ## It is COM7 on my laptop, might be different on other devices
# bluetooth_serial = serial.Serial("COM7", 921600)

# def send_command(frequency, steps, direction):
#     command = f"{frequency},{steps},{int(direction)}\n"
#     bluetooth_serial.write(command.encode())
#     print("Sent command:", command)
#     time.sleep(0.1)

# def listen_for_message():
#     while True:
#         if bluetooth_serial.in_waiting > 0:
#             message = bluetooth_serial.readline().decode().strip()
#             if message == "LIMIT_SWITCH_TRIGGERED":
#                 print("Limit Switch triggered")
#             else:
#                 print("Received message: ", message)
#         time.sleep(0.1)

# send_command(300, 1000, True)
# listen_for_message()