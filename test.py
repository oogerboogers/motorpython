import sys
import time
import stagecontroller

def main():
    # Initialize and connect to the stage controller
    controller = stagecontroller.StageController(port='COM3', baudrate=9600, timeout=1)
    controller.connect()

    # Home the stage initially
    controller.home()

    while True:
        try:
            # Request user input
            command = input("Enter command (or coordinates as X Y Z): ").strip()

            if command.lower() == 'home':
                # Home the stage
                print("Homing the stage...")
                controller.home()
            elif command.lower() == 'homex':
                # Home the stage
                print("Homing the stage along x")
                controller.home(homeY=False, homeZ = False)
            elif command.lower() == 'homey':
                # Home the stage
                print("Homing the stage along y")
                controller.home(homeX = False, homeZ = False)
            elif command.lower() == 'homez':
                # Home the stage
                print("Homing the stage along z")
                controller.home(homeX = False, homeY = False)
            else:
                # Parse coordinates from the command input
                coords = command.split()
                if len(coords) == 3:
                    try:
                        x, y, z = map(float, coords)
                        # Move the stage to the specified coordinates
                        print(f"Moving to coordinates ({x}, {y}, {z})...")
                        controller.move_to(x, y, z, interval=2)
                    except ValueError:
                        print("Invalid coordinates. Please enter three numeric values.")
                else:
                    print("Invalid input. Please enter 'home' or three numeric values separated by spaces.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
