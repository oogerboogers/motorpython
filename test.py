import sys
import time
import stagecontroller
import cv2 as cv


def gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, stepSize, interval = 2, delay = 2):
    diffX = endX - startX
    diffY = endY - startY
    diffZ = endZ - startZ

    stepsX = int(diffX / stepSize)
    stepsY = int(diffY / stepSize)
    stepsZ = int(diffZ / stepSize)

    camera = cv.VideoCapture(0)

    for i in range(stepsX + 1):
        for j in range(stepsY + 1):
            for k in range(stepsZ + 1):
                x = startX + i * stepSize
                y = startY + j * stepSize
                z = startZ + k * stepSize

                print("Moving to coordinates ({}, {}, {})".format(x, y, z))
                controller.move_to(x, y, z, interval)
                # Take picture here
                time.sleep(delay)
                takePicture(controller, camera)

    camera.release()

                
def takePicture(controller, cameraIn = None):
    x = controller.get_position()[0]
    y = controller.get_position()[1]
    z = controller.get_position()[2]

    print("Taking picture at coordinates ({}, {}, {})".format(x, y, z))
    # Take picture here

    try:
        if cameraIn:
            camera = cameraIn
        else:
            camera = cv.VideoCapture(0)
        img = camera.read()[1]
        # Save image
        filename = "images/image_{}_{}_{}.png".format(x, y, z)
        cv.imwrite(filename, img)
        
        if not cameraIn:
            camera.release()
    except:
        print("Error taking picture")
        print(sys.exc_info()[0])
        return




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

            if command.lower() == 'picture':
                takePicture(controller)
            elif command.lower() == 'grid':
                # query user
                #print("Enter start x, y, z/n")
                startPos = input("Enter start x y z: ").strip().split()
                if len(startPos) != 3:
                    print("Invalid input. Please enter three numeric values separated by spaces.")
                    continue

                #print("Enter end x, y, z/n")
                endPos = input("Enter end x y z: ").strip().split()
                if len(endPos) != 3:
                    print("Invalid input. Please enter three numeric values separated by spaces.")
                    continue

                stepSize = float(input("Enter step size: "))

                interval = 2
                delay = int(input("Enter delay: "))

                startX, startY, startZ = map(float, startPos)
                endX, endY, endZ = map(float, endPos)

                gridTakePicture(controller, startX, startY, startZ, endX, endY, endZ, stepSize, interval, delay)

            elif command.lower() == 'home':
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
