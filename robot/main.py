#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_D, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4

from ev3dev2.wheel import EV3EducationSetTire
from ev3dev2.motor import LargeMotor, MoveTank, MoveDifferential, MediumMotor
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor

from ev3dev2.button import Button
from time import sleep
from ev3dev.ev3 import Sound

import sys
import grid
import bluetooth

map = [[grid.Grid() for x in range(9)] for y in range(9)]

# 0 - Up
# 1 - Right
# 2 - Left
# 3 - Down
universal_direction = 0

# def move_to_next_grid():
#  BU METHODTA VERILEN IKI KONUMA GORE GIDILMESI GEREKEN YON BULUNACAK
#  SUAN ROBOTUMUZUN HALIHAZIRDA NEREYE BAKTIGINI SUANA KADAR TRACE ETMEMIZ GEREKIYORDU
#  BU IKI YONU BIRBIRINDEN CIKARTARAK ROBOTUMUZUN NE KADAR DONMESI GEREKTIGINI BULUCAZ
#  HER YONUN 0,1,2,3 DEGERLERI OLUCAK. BIRBIRINDEN CIKARINCA NE KADAR DONULECEGI ANLASILACAK
def move_to_next_grid(inital_pos, next_pos):
    print("asldka")

def check_wall(ultrasonicS, ultrasonicM, wall_direction):
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


def mapping(socket, colorS, ultrasonicS, ultrasonicM, moveDiff, moveTank):
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

        if check_wall(ultrasonicS, ultrasonicM, 2):  
            map[x][y].left_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x-1][y].visited:
                non_visited_grids += 1
                next_grid[0] = x-1
        
        if not map[x][y].visited:
            map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1


        if check_wall(ultrasonicS, ultrasonicM, 1):
            map[x][y].right_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x+1][y].visited:
                non_visited_grids += 1
                next_grid[0] = x+1
            
        if not map[x][y].visited:
            map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1

        if check_wall(ultrasonicS, ultrasonicM, 0):
            map[x][y].up_wall = True
            map[x][y].non_visited_neighbors -= 1
        else:
            if not map[x][y+1].visited:
                non_visited_grids += 1
                next_grid[1] = y+1
        
        if not map[x][y].visited:
            map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1


        if not map[x][y].visited:
            map[x][y].visited = True
            non_visited_grids -= 1

        if map[x][y].non_visited_neighbors != 0:
            x = map[x][y].last_move[0]
            y = map[x][y].last_move[1]
        else:
            map[next_grid[0]][next_grid[1]].last_move[0] = x
            map[next_grid[0]][next_grid[1]].last_move[1] = y
            x = next_grid[0]
            y = next_grid[1]

        # map[x][y] ye git 

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


    moveTank = MoveTank(OUTPUT_A, OUTPUT_D)
    moveDiff = MoveDifferential(OUTPUT_A, OUTPUT_D, EV3EducationSetTire, 115)

    ultrasonicS = UltrasonicSensor()
    colorS = ColorSensor()
    ultrasonicM = MediumMotor(OUTPUT_B)

    ultrasonicS.mode = 'US-DIST-CM'
    colorS.mode = 'COL-COLOR'

    server_mac = '88:B1:11:79:C5:F6'
    port = 4 
    btn = Button()

    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.connect((server_mac, port))
    
    # while not btn.any():
    #     sleep(0.05)

    # BASILAN BUTONU BUL

    mapping(s, colorS, ultrasonicS, ultrasonicM, moveDiff, moveTank)
