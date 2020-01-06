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
wheelBase = 115

rightMotor = LargeMotor(OUTPUT_D)
leftMotor = LargeMotor(OUTPUT_A)
moveTank = MoveTank(OUTPUT_A, OUTPUT_D)
moveDiff = MoveDifferential(OUTPUT_A, OUTPUT_D, EV3EducationSetTire, 115)

ultrasonicS = UltrasonicSensor()
ultrasonicM = MediumMotor(OUTPUT_C)
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

def turn90DegreeTank(turnDegree):
    if turnDegree > 0:
        for _ in range(int(turnDegree/90)):
            rightMotorThread = threading.Thread(target=turn90DegreeMotor, args=(rightMotor, wheelDiameter, wheelBase, -speed))
            leftMotorThread = threading.Thread(target=turn90DegreeMotor, args=(leftMotor, wheelDiameter, wheelBase, speed))
            rightMotorThread.start()
            leftMotorThread.start()
            rightMotorThread.join()
            leftMotorThread.join()
    elif turnDegree < 0:
        for _ in range(int(abs(turnDegree/90))):
            rightMotorThread = threading.Thread(target=turn90DegreeMotor, args=(rightMotor, wheelDiameter, wheelBase, speed))
            leftMotorThread = threading.Thread(target=turn90DegreeMotor, args=(leftMotor, wheelDiameter, wheelBase, -speed))
            rightMotorThread.start()
            leftMotorThread.start()
            rightMotorThread.join()
            leftMotorThread.join()
    else:
        return
# ################################################################################################################# #
def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.
    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)
# ################################################################################################################# #

# MAPPING
map = [[grid.Grid() for x in range(9)] for y in range(9)]

unvisitedGridList = []

outfile = open('map', 'wb')
infile = open('map', 'rb')

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
    control = (-dx+1)%2
    target_direction = 0
    if control == 0:
        target_direction += (-dx+1)/2 * 2 + 1
    else:
        target_direction += (-dy+1)/2 * 2

    turn_number = (target_direction - current_direction) % 4 
    if turn_number == 3:
        turn_number = -1
    turn_degree = turn_number * 90
    
    turn90DegreeTank(turn_degree)
    current_direction = target_direction
    moveForwardTank(335)

def get_color():
    value = colorS.value()
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

    value = value / 10

    return value < 25


def orientation(current_grid, local_bias):
    # local_bias : 0 for checking the up wall, 1 for the right, 3 for the left
    # current_direction: the global bias of robot from the upward direction, 0 for up, 1,2,3 in cw

    global_bias = current_direction
    orientations = [[0,1], [1,0], [0,-1], [-1,0]] 

    heading = orientations[int((local_bias + global_bias) % 4)]
    next_grid = [current_grid[0] + heading[0], current_grid[1] + heading[1]]

    return next_grid


def check_side(current_grid, wall_direction, next_grid, unvisited_grids):
    global map
    wall_detected = check_wall(wall_direction)
    debug_print("######INSIDE CHECK_SIDE######")
    debug_print("Checking " + str(wall_direction))
    x = current_grid[0]
    y = current_grid[1]
    debug_print("X: " + str(x) + " Y: " + str(y))
    if wall_detected:
        debug_print("Wall Detected")
        map[x][y].wall[int((current_direction + wall_direction)%4)] = True
        if not map[x][y].visited:
            map[x][y].unvisited_neighbors -= 1
        debug_print("u_n: " + str(map[x][y].unvisited_neighbors))
    else:  # if the visible grid is not visited, acknowledge that the mapping task is incomplete

        visible_grid = orientation(current_grid, wall_direction)
        debug_print("Not Wall Detected, visible_grid: " + str(visible_grid))
        if not map[visible_grid[0]][visible_grid[1]].visited: 
            next_grid = visible_grid

            temp = visible_grid[0] * 10 + visible_grid[1]
            if not temp in unvisitedGridList:
                unvisitedGridList.append(temp)
                unvisited_grids += 1
            
        
        if not map[x][y].visited:       
            # decrement the visible grid's n_v_n
            map[visible_grid[0]][visible_grid[1]].unvisited_neighbors -= 1 

    return next_grid, unvisited_grids

def encode_message_mapping(g, pos):
    # m_xyurdlc where x and y are the positions; u, r, d, l are walls and c is color
    message = "m_"
    message = message + str(pos[0]) + str(pos[1]) 

    for w in g.wall:
        if w:
            message += "t"
        else:
            message += "f" 
        
    message += str(g.color)

    return message

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
        debug_print("***************************************************")
        debug_print("Inside Mapping, Current Grid: " + str(current_grid))
        
        if map[x][y].unvisited_neighbors == 0:
            debug_print("STUCK, unvisited_neighbors == 0")
            check_neighbors = False
            if map[x][y].visited: # if itself and all neighbors are visited, go one step back in DFS route.
                next_grid = [map[x][y].last_move[0], map[x][y].last_move[1]]
                x = next_grid[0]
                y = next_grid[1]
                move_to_next_grid(current_grid, next_grid)
                continue

        # get and set the color of the current grid
        color = get_color()
        map[x][y].color = color
        debug_print("Color: " + str(color))

        # if the color is black, send information, go one step back
        if color == 0 or color == 1:
            debug_print("color == BLACK")
            map[x][y].visited = True
            map[map[x][y].last_move[0]][map[x][y].last_move[1]].unvisited_neighbors -= 1
            temp = unvisited_grids - 1
            for side in ["left","right","up"]:
                _, _ = check_side(current_grid, direction[side], next_grid, unvisited_grids)
            next_grid = map[x][y].last_move
            message = encode_message_mapping(map[x][y], current_grid)
            socket.send(message)
            x = next_grid[0]
            y = next_grid[1]
            unvisited_grids = temp
            
            if unvisited_grids == 0:
                Sound.beep()
                Sound.beep()
                Sound.beep()
                continue
            move_to_next_grid(current_grid, next_grid)
            continue
        
        if check_neighbors:
            for side in ["left","right","up"]:
                next_grid, unvisited_grids = check_side(current_grid, direction[side], next_grid, unvisited_grids)
                debug_print("After checking " + side + " next grid = " + str(next_grid) + " u_g : " + str(unvisited_grids))
            debug_print("U_N: " + str(map[x][y].unvisited_neighbors))
        # If the current grid is not visited before, then mark it visited
        if not map[x][y].visited: 
            map[x][y].visited = True
            map[map[x][y].last_move[0]][map[x][y].last_move[1]].unvisited_neighbors -= 1
            unvisited_grids -= 1
            debug_print("Now visiting " + str(x) + " " + str(y))
            message = encode_message_mapping(map[x][y], current_grid)
            socket.send(message)

            # THE MAPPING MODE SHOULD TERMINATE
            if unvisited_grids == 0:
                Sound.beep()
                Sound.beep()
                Sound.beep()
                continue
        
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
    pickle.dump(map, outfile)
    outfile.close()

# LOCALIZATION
def move_particle(particle, heading):
    orientations = [[0,1], [1,0], [0,-1], [-1,0]] 
    d_pos = orientations[heading]
    i = particle[0] + d_pos[0] 
    j = particle[1] + d_pos[1] 
    movement = [i-particle[0], j-particle[1]]
    d = orientations.index(movement)

    return [i, j, localization[particle[i]][particle[j]].color, d]

def move_robot(heading):
    turn_number = heading
    if turn_number == 3:
        turn_number = -1
    turn_degree = turn_number * 90
    
    turn90DegreeTank(turn_degree)
    moveForwardTank(335)

def encode_message_localization(heading, color, up, right, left):
    # l_hcurl000
    message = "l_" + str(heading) + str(color)
    message += "t" if up else "f"
    message += "t" if right else "f"
    message += "t" if left else "f"

    message += "000"

    return message

def localization(socket):
    localization_map = pickle.load(infile)
    infile.close()

    particles = []

    for i in range(7):
        for j in range(7):
            if localization_map[i+1][j+1].visited:
                for d in range(4):
                    particles.append([i, 8-j, localization_map[i][j].color, d])
    
    localized = False
    while not localized:
        current_color = get_color()
        up = check_wall(direction["up"])
        right = check_wall(direction["right"])
        left = check_wall(direction["left"])
        expected_state = [up, right, left, current_color]

        heading = 0
        if left: 
            heading = 3
        if right: 
            heading = 1
        if up:
            heading = 0
        
        message = encode_message_localization(heading, current_color, up, right, left)
        socket.send(message)

        for particle in particles:
            not_removed = True
            particle_state = [0,0,0,0]
            particle_state[0] = localization_map[particle[0]][particle[1]].wall[(0+particle[3])%4]
            particle_state[1] = localization_map[particle[0]][particle[1]].wall[1+particle[3])%4]
            particle_state[2] = localization_map[particle[0]][particle[1]].wall[3+particle[3])%4]
            particle_state[3] = particle[2]
            for i in range(4):
                if particle_state[i] != expected_state[i]:
                    particles.remove(particle)
                    not_removed = False
                    if len(particles) == 1:
                        localized = True
                        break
            if localized:
                break
            if not_removed:
                particle = move_particle(particle, heading)
        if localized:
                continue
        move_robot(heading)


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

    while True:
        while not btn.any():
            sleep(0.05)
            
        if btn.up():
            mapping(s)
        elif btn.down():
            localization(s)