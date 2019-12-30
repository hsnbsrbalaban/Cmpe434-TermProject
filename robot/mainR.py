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

direction = {  
  "up": 0,
  "right": 1,
  "down": 2,
  "left": 3
}

current_direction = direction["up"]

def move_to_next_grid(initial_pos, next_pos):
    global current_direction

    dx = next_pos[0] - initial_pos[0]
    dy = next_pos[1] - initial_pos[1]

    target_direction = -1 * (dx - 1) + (-dy +2) 
    turn_number = (target_direction - current_direction) % 4 
    if turn_number == 3:
        turn_number = -1
    turn_degree = turn_number * 90
    # THIS CAN BE REPLACED BY TURN90DEGREETANK METHOD SINCE MOVEDIFF IS NOT OPTIMIZED
    moveDiff.turn_to_angle(20, turn_degree)

    current_direction = target_direction

    moveForwardTank(330)

def get_color():
    value = colorS.color_name()
    sleep(0.1)
    return value

# returns True if there is a wall just next to the robot
def check_wall(wall_direction):
    value = 0
    if wall_direction == direction["up"]:
        value = ultrasonicS.value()
        sleep(0.1)
    elif wall_direction == direction["right"]:
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


def orientation(current_grid, local_bias):
    # local_bias : 0 for checking the up wall, 1 for the right, 3 for the left
    # current_direction: the global bias of robot from the upward direction, 0 for up, 1,2,3 in cw

    global_bias = current_direction
    orientations = [[0,1], [1,0], [0,-1], [-1,0]] 

    heading = orientations[(local_bias + global_bias) % 4]
    next_grid = [current_grid[0] + heading[0], current_grid[1] + heading[1]]

    return next_grid


def check_side(current_grid, wall_direction, next_grid, unvisited_grids):
    global map
    wall_detected = check_wall(wall_direction)
    x = current_grid[0]
    y = current_grid[1]

    if wall_detected:
            map[x][y].wall[wall_direction] = True
            map[x][y].unvisited_neighbors -= 1
    else:  # if the visible grid is not visited, acknowledge that the mapping task is incomplete

        visible_grid = orientation([x,y], wall_direction)
        if not map[visible_grid[0]][visible_grid[1]].visited: 
            unvisited_grids += 1
            next_grid = visible_grid
        
        if not map[x][y].visited:       
            # decrement the visible grid's n_v_n
            map[next_grid[0]][next_grid[1]].unvisited_neighbors -= 1 

    return next_grid, unvisited_grids

def mapping(socket):
    global map
    unvisited_grids = 1
    x = y = 4

    # we assume that there is a wall behind the start location
    map[x][y].unvisited_neighbors = 3
    map[x][y].wall[direction["down"]] = True 
    
    while(unvisited_grids > 0):

        current_grid = [x,y]  # address of current grid
        next_grid = [x,y]  # address of next grid that will be visited
        check_neighbors = True  # the boolean value if we need to check neighbors

        
        if map[x][y].unvisited_neighbors == 0:
            check_neighbors = False
            if map[x][y].visited: # if itself and all neighbors are visited, go one step back in DFS route.
                next_grid = [map[x][y].last_move[0], map[x][y].last_move[1]]
                move_to_next_grid(current_grid, next_grid)
                continue

        # get and set the color of the current grid
        color = get_color()
        map[x][y].color = color

        # if the color is black, send information, go one step back
        if color == "Black":
            map[x][y].visited = True
            temp = unvisited_grids - 1
            for side in ["left","right","up"]:
                _, _ = check_side(current_grid, direction[side], next_grid, unvisited_grids)
            next_grid = map[x][y].last_move
            unvisited_grids = temp
            move_to_next_grid(current_grid, next_grid)
            continue
        
        if check_neighbors:
            for side in ["left","right","up"]:
                next_grid, unvisited_grids = check_side(current_grid, direction[side], next_grid, unvisited_grids)

        # If the current grid is not visited before, then mark it visited
        if not map[x][y].visited: 
            map[x][y].visited = True
            unvisited_grids -= 1
            # BLUETOOTH COMMUNICATION SHOULD OCCUR HERE!
            s.send(get_color())
            if unvisited_grids == 0:
                print("BEEP! BEEP! BEEP!")
                # THE MAPPING MODE SHOULD TERMINATE

        
        if map[x][y].unvisited_neighbors > 0:  
            # if you can go to an unvisited grid, save its last_move for the sake of DFS
            map[next_grid[0]][next_grid[1]].last_move[0] = x
            map[next_grid[0]][next_grid[1]].last_move[1] = y
        else: 
            # if all neighbors are visited, go back through DFS route
            next_grid = map[x][y].last_move
            
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
