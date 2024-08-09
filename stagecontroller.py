import serial
import time
import math

STEPS_PER_MM = 200 * 32 / 2  # 200 steps per revolution, 32 microsteps, 2 mm per revolution
MAX_STEPS_PER_COMMAND = 32767  # 16-bit unsigned integer, 2 bytes
HOME_AMOUNT_X = 100 * STEPS_PER_MM
HOME_AMOUNT_Y = 100 * STEPS_PER_MM
HOME_AMOUNT_Z = 20 * STEPS_PER_MM

class StageController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

        self.current_position = [0, 0, 0]

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print("Connected to Arduino")
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")

    def read_message(self):
        if self.ser:
            return self.ser.readline().decode().strip()
        else:
            print("Serial connection not established.")
            return None

    def send_command(self, command):
        if self.ser:
            self.ser.write(command.encode())
        else:
            print("Serial connection not established.")
            return None

    def close(self):
        if self.ser:
            self.ser.close()
            print("Connection closed")

    def wait_until_done_moving(self):
        doneX = False
        doneY = False
        doneZ = False
        while True:
            message = self.read_message()
            message = message[0]
            if message == 'x':
                doneX = True
            elif message == 'y':
                doneY = True
            elif message == 'z':
                doneZ = True
            else:
                pass

            if doneX and doneY and doneZ:
                break

    def moveBy(self, stepsX, stepsY, stepsZ, interval = 2, home = False):
        "Move the stage by the specified number of steps"
        
        directionX = '1' if stepsX > 0 else '0'
        directionY = '1' if stepsY > 0 else '0'
        directionZ = '1' if stepsZ > 0 else '0'

        stepsX = abs(stepsX)
        stepsY = abs(stepsY)
        stepsZ = abs(stepsZ)

        cycleX = math.floor(stepsX / MAX_STEPS_PER_COMMAND)
        cycleY = math.floor(stepsY / MAX_STEPS_PER_COMMAND)
        cycleZ = math.floor(stepsZ / MAX_STEPS_PER_COMMAND)

        remainderX = stepsX % MAX_STEPS_PER_COMMAND
        remainderY = stepsY % MAX_STEPS_PER_COMMAND
        remainderZ = stepsZ % MAX_STEPS_PER_COMMAND

        home = '0' if home else '1'

        # Send the command to move the stage
        maxCycle = max(cycleX, cycleY, cycleZ)
        for i in range(maxCycle):
            # command: a [steps] [direction] [interval] [home] [motor]
            commandX = f"a {MAX_STEPS_PER_COMMAND} {directionX} {interval} {home} 0\n"
            commandY = f"a {MAX_STEPS_PER_COMMAND} {directionY} {interval} {home} 1\n"
            commandZ = f"a {MAX_STEPS_PER_COMMAND} {directionZ} {interval} {home} 2\n"
            self.send_command(commandX)
            self.send_command(commandY)
            self.send_command(commandZ)

            # Wait for the stage to finish moving before sending the next command.
            # Should recieve x, y, z, when the stage is done moving.
            self.wait_until_done_moving()
            
        # Send the command to move the stage by the remainder
        commandX = f"a {remainderX} {directionX} {interval} {home} 0\n"
        commandY = f"a {remainderY} {directionY} {interval} {home} 1\n"
        commandZ = f"a {remainderZ} {directionZ} {interval} {home} 2\n"

        self.send_command(commandX)
        self.send_command(commandY)
        self.send_command(commandZ)
        self.wait_until_done_moving()

    def home(self):
        "Move the stage to the home position"

        homeX = -HOME_AMOUNT_X
        homeY = -HOME_AMOUNT_Y
        homeZ = -HOME_AMOUNT_Z

        self.moveBy(homeX, homeY, homeZ, home=True)
        self.current_position = [0, 0, 0]

    def move_to(self, x, y, z):
        "Move the stage to the specified position in mm"

        moveX = x - self.current_position[0]
        moveY = y - self.current_position[1]
        moveZ = z - self.current_position[2]

        # Convert to steps
        moveX = math.round(moveX * STEPS_PER_MM)
        moveY = math.round(moveY * STEPS_PER_MM)
        moveZ = math.round(moveZ * STEPS_PER_MM)

        self.moveBy(moveX, moveY, moveZ)
        
        # Update the current position
        self.current_position[0] += moveX / STEPS_PER_MM
        self.current_position[1] += moveY / STEPS_PER_MM
        self.current_position[2] += moveZ / STEPS_PER_MM
 







        