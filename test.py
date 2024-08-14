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
                
                autoFocus(controller)
                #takePicture(controller, camera)

    camera.release()

                
def takePicture(controller, cameraIn = None):
    x, y, z = controller.get_position()

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
#built for specific thing, dont use i think
def autoFocusNoThreshold(controller, image, originalBlur, camera, haveDone = False, cameraIn = None, direction = 1):
    x, y, z = controller.get_position()
    blur = cv.Laplacian(image, cv.CV_64F).var()
    controller.move_to(x, y, z-direction)
    if blur < originalBlur and haveDone:
        controller.move_to(x, y, z+direction)
        takePicture(controller)
        return
    elif blur < originalBlur:
        direction = direction*-1
        autoFocusNoThreshold(controller, camera.read()[1], blur, camera, True, None, direction)
    autoFocusNoThreshold(controller, camera.read()[1], blur, camera, haveDone)



def estimate_z_change(current_blur, target_blur, direction, z_step):
    blur_difference = abs(target_blur - current_blur)
    z_change = int(blur_difference / 100)
    z_change = max(z_change, 0.2)
    return direction * z_change * z_step

#might be a boolean error, prob not 
def find_direction(controller, camera):
    x, y, z = controller.get_position()
    controller.move_to(x, y, z+1)
    blur1 = cv.Laplacian(camera.read()[1], cv.CV_64F)
    controller.move_to(x, y, z-2)
    blur2 = cv.Laplacian(camera.read()[1], cv.CV_64F)
    #97 percent sure it is more blurry if it is less
    return 1 if blur1 > blur2 else -1

def autoFocus(controller, target_blur=300, direction=1, z_step=5,cameraIn = None):
    if cameraIn:
        camera = cameraIn
    else:
        camera = cv.VideoCapture(0)
    image = camera.read()[1]
    x, y, z = controller.get_position()
    current_blur = cv.Laplacian(image, cv.CV_64F).var()

    if abs(current_blur - target_blur) <= 5:
        takePicture(controller)
        return
    
    estimated_z_change = estimate_z_change(current_blur, 300, direction, z_step)
    controller.move_to(x, y, z + estimated_z_change)
    old_blur = 0
    direction = find_direction(controller, camera)
    while True:
        if z_step < 1/32:
            print("Failed Zoom-in, image might be blurry at ({}, {}, {})".format(x, y, z))
            takePicture(controller)
            break
        image = camera.read()[1]
        current_blur = cv.Laplacian(image, cv.CV_64F).var()

        if abs(current_blur) > 290:
            takePicture(controller)
            break
        
        controller.move_to(x, y, z + direction * z_step)
        if current_blur < old_blur:
            z_step = z_step/2
            direction = direction*-1
        old_blur = current_blur
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
