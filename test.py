# Test stagecontroller

import sys
import time

import stagecontroller;

controller = stagecontroller.StageController(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

controller.connect()

controller.moveBy(100, 100, 100)