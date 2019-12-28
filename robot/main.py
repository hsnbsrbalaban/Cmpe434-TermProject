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
# ################################################################################################################# #
# MOTOR METHODS
speed = 20
wheelDiameter = 56
wheelBase = 120

rightMotor = LargeMotor(OUTPUT_D)
leftMotor = LargeMotor(OUTPUT_A)
moveTank = MoveTank(OUTPUT_A, OUTPUT_D)
moveDiff = MoveDifferential(OUTPUT_A, OUTPUT_D, EV3EducationSetTire, 115)

ultrasonicS = UltrasonicSensor()
ultrasonicM = MediumMotor(OUTPUT_B)
colorS = ColorSensor()

ultrasonicS.mode = 'US-DIST-CM'
colorS.mode = 'COL-COLOR'

def calculateRotationsForDistance(distance, wheelDiameter):
    return distance/(math.pi*wheelDiameter)

def moveForwardMotor(motor, wheelDiameter, distance):
    motor.on_for_rotations(speed, calculateRotationsForDistance(distance, wheelDiameter))

def moveForwardTank(distance):
    rightMotorThread = threading.Thread(target=moveForwardMotor, args=(rightMotor, wheelDiameter, distance))
    leftMotorThread = threading.Thread(target=moveForwardMotor, args=(leftMotor, wheelDiameter, distance))
    rightMotorThread.start()
    leftMotorThread.start()
    rightMotorThread.join()
    leftMotorThread.join()

def calculateRotationsFor90DegreeTurn(wheelBase, wheelDiameter):
    return ((wheelBase*math.pi)/4.0)/(math.pi*wheelDiameter)

def turn90DegreeMotor(motor, wheelDiameter, wheelBase, speed):
    motor.on_for_rotations(speed, calculateRotationsFor90DegreeTurn(wheelBase, wheelDiameter))

def turn90DegreeTank():
    rightMotorThread = threading.Thread(target=turn90DegreeMotor, args=(rightMotor, wheelDiameter, wheelBase, -speed))
    leftMotorThread = threading.Thread(target=turn90DegreeMotor, args=(leftMotor, wheelDiameter, wheelBase, speed))
    rightMotorThread.start()
    leftMotorThread.start()
    rightMotorThread.join()
    leftMotorThread.join()
# ################################################################################################################# #

# MAPPING
map = [[grid.Grid() for x in range(9)] for y in range(9)]

current_direction = 0 # 0-up, 1-right, 2-down, 3-left

def move_to_next_grid(initial_pos, next_pos):
    global current_direction

    dx = next_pos[0] - initial_pos[0]
    dy = next_pos[1] - initial_pos[1]

    ideal_direction = -1 * (dx - 1) + (-dy +2)
    turn_number = (ideal_direction - current_direction) % 4 
    if turn_number == 3:
        turn_number = -1
    turn_degree = turn_number * 90
    # THIS CAN BE REPLACED BY TURN90DEGREETANK METHOD SINCE MOVEDIFF IS NOT OPTIMIZED
    moveDiff.turn_to_angle(20, turn_degree)

    current_direction = ideal_direction

    moveForwardTank(330)

def get_color():
    value = colorS.color_name()
    sleep(0.1)
    return value

def check_wall(wall_direction):
    # 0 - Up, 1 - Right, 2 - Left
    value = 0
    if wall_direction == 0:
        value = ultrasonicS.value()
        sleep(0.1)
    elif wall_direction == 1:
        ultrasonicM.on_for_degrees(20, 90)
        sleep(0.1)
        value = ultrasonicS.value()
        sleep(0.1)
        ultrasonicM.on_for_degrees(20, -90)
    else:
        ultrasonicM.on_for_degrees(20, -90)
        sleep(0.1)
        value = ultrasonicS.value()
        sleep(0.1)
        ultrasonicM.on_for_degrees(20, 90)

    return value < 20


def mapping(socket):
    non_visited_grids = 1
    x = y = 4

    # we assume that the wall begind the 
    map[x][y].non_visited_neighbors = 3
    map[x][y].down_wall = True
    
    while(non_visited_grids > 0):
        if map[x][y].non_visited_neighbors == 0:
            current_grid = [x,y]
            target_grid = [map[x][y].last_move[0], map[x][y].last_move[1]]
            
            move_to_next_grid(current_grid, target_grid)
            continue
        
        color = colorS.color_name()
        map[x][y].color = color
        if color == "Black":
            current_grid = [x,y]
            target_grid = [map[x][y].last_move[0], map[x][y].last_move[1]]
            non_visited_grids -= 1
            
            move_to_next_grid(current_grid, target_grid)
            continue

        next_grid = [x,y]

        if check_wall(2):   # check Left wall
            map[x][y].left_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x-1][y].visited:  # if the visible grid is not visited, then acknowledge that the mapping is incomplete
                non_visited_grids += 1
                next_grid[0] = x-1
        
            if not map[x][y].visited:       # decrement the visible grid's n_v_n
                map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1 # decrementing n_v_n



        if check_wall(1):  # check Right wall
            map[x][y].right_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x+1][y].visited:
                non_visited_grids += 1
                next_grid[0] = x+1
            
            if not map[x][y].visited:
                map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1


        if check_wall(0): # check Up wall
            map[x][y].up_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x][y+1].visited: 
                non_visited_grids += 1
                next_grid[1] = y+1
        
            if not map[x][y].visited:
                map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1


        if not map[x][y].visited: # If the current grid not visited before, then mark it visited
            map[x][y].visited = True
            # BLUETOOTH COMMUNICATION SHOULD OCCUR HERE!
            s.send(get_color())
            non_visited_grids -= 1

        if map[x][y].non_visited_neighbors != 0: # if all neighbors are visited, go back by DFS route
            current_grid = [x,y]
            target_grid = [map[x][y].last_move[0], map[x][y].last_move[1]]
            
            move_to_next_grid(current_grid, target_grid)
        else:                # if you go to a nonvisited grid, save its last_move due to DFS, and go there
            current_grid = [x,y]
            map[next_grid[0]][next_grid[1]].last_move[0] = x
            map[next_grid[0]][next_grid[1]].last_move[1] = y
            x = next_grid[0]
            y = next_grid[1]

            move_to_next_grid(current_grid, next_grid)

if __name__ == "__main__":
    # bluetooth iletişim olacak, robot->pc string gönderimi robotta encode bilgisayarda decode edilecek

    # at first,
    # pc should only wait for bluetooth message from robot
    # robot should send which button is pressed

    # in any mode, 
    # pc should check first if any button is pressed after decoding the message
    # if not any button pressed, then should apply the command given by robot in
    # corresponding mode's method.

    # string encoding should be:
    # mapping, taskexecution, idle, reset

    # string encodings: 
    # for buttons : pressed_m, pressed_t, pressed_i, pressed_r,
    # in mapping mode: m_<i>_<j>_<color_num>_<wall_encoded> OR m_already OR m_is_over

    server_mac = '88:B1:11:79:C5:F6'
    port = 4 
    btn = Button()

    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.connect((server_mac, port))
    
    # while not btn.any():
    #     sleep(0.05)

    # BASILAN BUTONU BUL

    mapping(s)
