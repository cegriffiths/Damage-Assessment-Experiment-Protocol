#!/usr/bin/env python3

import socket
import sys
import time
import threading

##Dashboard Commands
# This is the IP address of the robot.
ROBOT_IP = "10.42.0.30" #Double check this
SERVER_IP = "10.42.0.1"
DASHBOARD_PORT = 29999
ROBOT_PORT = 30001 #Same as from the URScript

class Robot:
    def __init__(self, ROBOT_IP, DASHBOARD_PORT, ROBOT_PORT):
        self.ROBOT_IP = ROBOT_IP
        self.SERVER_IP = SERVER_IP
        self.DASHBOARD_PORT = DASHBOARD_PORT
        self.ROBOT_PORT = ROBOT_PORT
        self.timeout = 5
        self.dash_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((SERVER_IP, ROBOT_PORT))
        self.server_socket.listen(3)

    def connect(self):
        self.dash_socket.settimeout(self.timeout)
        self.dash_socket.connect((self.ROBOT_IP, self.DASHBOARD_PORT))
        self.dash_socket.recv(1096)
        print("Connected to dashboard.")

    def close(self):
        self.dash_socket.close()
        self.server_socket.close()
        print("Closed connections.")

    #Interact with Dashboard
    def send_command(self, command):
        try:
            self.dash_socket.sendall((command + '\n').encode())
            return(self.get_reply())
        except (ConnectionResetError, ConnectionAbortedError):
            print("The connection was lost to the robot. Please connect and try running again.")
            self.close()
            sys.exit()

    def get_reply(self):
        """
        read one line from the socket
        :return: text until new line
        """
        collected = b''
        while True:
            part = self.dash_socket.recv(1)
            if part != b"\n":
                collected += part
            elif part == b"\n":
                break
        return collected.decode("utf-8")
    
    def send_PnPData(self, num_picks, num_sensors, coords):
        sent_num_picks = False
        sent_num_sensors = False
        sent_coords = False
        try:
            while not (sent_num_picks and sent_num_sensors and sent_coords):
                collected = b''
                while True:
                    part = client.recv(1)
                    if part != b'\n':
                        collected += part
                    elif part == b'\n':
                        break
                    
                request = collected.decode('utf-8')
                print(f"Received request: {request}")
                time.sleep(0.5)
            
                #Check request starts with GET
                if request.startswith("GET"):
                    #Get Var name
                    var_name = request.split(" ")[1]
                    match var_name:
                        case "NUM_PICKS":
                            message = f"{var_name} {num_picks}\n"
                            client.send(message.encode())
                            print(f"Sent number of picks: {num_picks}")
                            sent_num_picks = True
                        case "NUM_SENSORS":
                            message = f"{var_name} {num_sensors}\n"
                            client.send(message.encode())
                            print(f"Sent number of sensors: {num_sensors}")
                            sent_num_sensors = True
                        case "POSITIONS":
                            for pos in coords:
                                message = "("
                                for p in pos:
                                    message += str(p)
                                    message += ","
                                message = message[:-1]
                                message += ")"
                                message += "\n"
                                client.send(message.encode())
                            print("Sent positions")
                            sent_coords = True
                        case _:
                            print("Unknown variable")
                else:
                    print("Unknown request")
            print("Sent all pnp data")
        except KeyboardInterrupt:
            print("Interrupted by user")

class RobotExt:
    def __init__(self, robot_ip, dashboard_port, robot_port):
        self.robot = Robot(robot_ip, dashboard_port, robot_port)
        self.robot.connect()

    def calibrate(self):
        remoteCheck = self.robot.send_command('is in remote control')
        if 'false' in remoteCheck:
            raise Exception('Robot is in local mode. Please set the robot to remote mode and try again.')

        print("Powering on robot")
        self.robot.send_command('power on')
        ready = False
        while not ready:
            ready = not [i for i in ['POWER_ON', 'POWER_OFF', 'BOOTING'] if i in self.robot.send_command('robotmode')]
            time.sleep(1)

        print("Releasing brakes")
        self.robot.send_command('brake release')
        ready = False
        while not ready:
            ready = 'RUNNING' in self.robot.send_command('robotmode')
            time.sleep(1)

        print("Loading Init Script")
        self.robot.send_command('load initialize.urp')
        time.sleep(1)
        print("Playing Init Script")
        self.robot.send_command('play')
        time.sleep(0.1)
        while('true' in self.robot.send_command('running')):
            time.sleep(1)

    def run(self, num_sensors, num_picks, sensor_positions):
        print("Loading PnP Script")
        self.robot.send_command('load pick_and_place.urp')
        time.sleep(1)
        print("Playing PnP Script")
        self.robot.send_command('play')
        print("Waiting for connection from robot")
        while True:
            try:
                global client, address
                client, address = self.robot.server_socket.accept()
                print(f"Connection from {address}")        
                break
            except KeyboardInterrupt:
                print("Closing connection")
                self.robot.close()
                sys.exit()

        print("Sending PnP Data")
        self.robot.send_PnPData(num_picks, num_sensors, sensor_positions)
        
        # Start a new thread to monitor the serial communication
        self.monitor_thread = threading.Thread(target=self.monitor_serial)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_serial(self):
        try:
            while True:
                collected = b''
                while True:
                    part = client.recv(1)
                    if part != b'\n':
                        collected += part
                    elif part == b'\n':
                        break

                status_update = collected.decode('utf-8')
                print(f"Status update from robot: {status_update}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Interrupted by user")
            self.robot.close()
            sys.exit()

if __name__ == '__main__':
    num_picks = 1
    num_sensors = 1
    sensor_positions = [
    [0.0718, -0.449, 0.1123, 0, 3.14, 0],
    ]

    robot_ext = RobotExt(ROBOT_IP, DASHBOARD_PORT, ROBOT_PORT)
    robot_ext.calibrate()
    robot_ext.run(num_sensors, num_picks, sensor_positions)

    # while True:
    #     pass