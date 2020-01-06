#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_D, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4

from ev3dev2.wheel import EV3EducationSetTire
from ev3dev2.motor import LargeMotor, MoveTank, MoveDifferential, MediumMotor
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor

from ev3dev2.button import Button
from time import sleep
from ev3dev.ev3 import Sound

import sys, threading, math, pickle, copy, bluetooth
import grid

