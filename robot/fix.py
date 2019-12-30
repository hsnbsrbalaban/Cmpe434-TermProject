
# IMPORTANT: this method should be called to assign next_grid in each wall check. IMPORTANT//



# globally, 
# 0: up, 1: right, 2: down, 3: left
# at base condition, the robot is in upward direction and it checks the up wall and the heading (0,+1)
# the heading to surrounding grids are, in clockwise: 
# (0,+1) (+1,0) (0,-1) (-1,0) in terms of current position(x,y)
# -------------
# depending on the deviation from the base case in clockwise, which is caused by
# local_bias or global_bias, the heading becomes one of these four values.
# -------
# local_bias: 
# global_bias: 
# eventually, the next_position <- current_position + heading 

def orientation(current_grid, local_bias):
    # local_bias : 0 for checking the up wall, 1 for the right, 3 for the left
    # current_direction: the global bias of robot from the upward direction, 0 for up, 1,2,3 in cw

    global_bias = current_direction
    orientations = [[0,1], [1,0], [0,-1], [-1,0]] 

    heading = orientations[(local_bias + global_bias)%4]

    next_grid = [current_grid[0] + heading[0], current_grid[1] + heading[1]]
    return next_grid



def check_side(current_grid, wall_direction, next_grid, non_visited_grids):
    wall_detected = check_wall(wall_direction)

    if wall_detected:
            map[x][y].wall[wall_direction] = True
            map[x][y].non_visited_neighbors -= 1
    else:  # if the visible grid is not visited, then acknowledge that the mapping is incomplete

        visible_grid = orientation([x,y], wall_direction)
        if not map[visible_grid[0]][visible_grid[1]].visited: 
            non_visited_grids += 1
            next_grid = visible_grid
            # decrement the visible grid's n_v_n
            if not map[x][y].visited:       
                # decrementing n_v_n
                map[next_grid[0]][next_grid[1]].non_visited_neighbors -= 1 

    return next_grid, non_visited_grids
