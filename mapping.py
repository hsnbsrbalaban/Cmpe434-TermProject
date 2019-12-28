#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_D, OUTPUT_C
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4

from ev3dev2.wheel import EV3EducationSetTire
from ev3dev2.motor import LargeMotor, MoveTank, MoveDifferential, MediumMotor
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor

from ev3dev2.button import Button
from time import sleep
from ev3dev.ev3 import Sound

import sys
import grid



map = [[grid.Grid() for x in range(7)] for y in range(7)]

# def move_to_next_grid():
#  BU METHODTA VERILEN IKI KONUMA GORE GIDILMESI GEREKEN YON BULUNACAK
#  SUAN ROBOTUMUZUN HALIHAZIRDA NEREYE BAKTIGINI SUANA KADAR TRACE ETMEMIZ GEREKIYORDU
#  BU IKI YONU BIRBIRINDEN CIKARTARAK ROBOTUMUZUN NE KADAR DONMESI GEREKTIGINI BULUCAZ
#  HER YONUN 0,1,2,3 DEGERLERI OLUCAK. BIRBIRINDEN CIKARINCA NE KADAR DONULECEGI ANLASILACAK


def mapping():
    non_visited_grids = 1
    x = y = 3

    map[x][y].non_visited_neighbors = 4
    # arkana bak: down wall update, wall degilse non_visited_neighbor++, non_visited_grids++
    # onune don ;)
    
    while(non_visited_grids > 0):
        if map[x][y].non_visited_neighbors == 0:
            x = map[x][y].last_move[0]
            y = map[x][y].last_move[1]
            # last_move a gore git
            continue
        
        # color = get_current_color()
        # map[x][y].color = color
        # if color == "black":
            # x = map[x][y].last_move[0]
            # y = map[x][y].last_move[1]
            # non_visited_grids -= 1
            # 
            # last_move a gore git
            # continue

        next_grid = [x,y]

    # if is_left_wall:
        map[x][y].left_wall = True
        map[x][y].non_visited_neighbors -= 1
    # else:
        if not map[x-1][y].visited:
            non_visited_grids += 1
            next_grid[0] = x-1
        
        if not map[x][y].visited:
            map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1


    # if is_right_wall:
        map[x][y].right_wall = True
        map[x][y].non_visited_neighbors -= 1
    # else:
        if not map[x+1][y].visited:
            non_visited_grids += 1
            next_grid[0] = x+1
        
        if not map[x][y].visited:
            map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1

    # if is_up_wall:
        map[x][y].up_wall = True
        map[x][y].non_visited_neighbors -= 1
    # else:
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
    moveTank = MoveTank(OUTPUT_A, OUTPUT_D)
    moveDiff = MoveDifferential(OUTPUT_A, OUTPUT_D, EV3EducationSetTire, 115)
    colorSMotor = MediumMotor(OUTPUT_C)

    ultrasonicS = UltrasonicSensor(INPUT_1)
    colorS = ColorSensor(INPUT_2)

    ultrasonicS.mode = 'US-DIST-CM'
    colorS.mode = 'COL-COLOR'