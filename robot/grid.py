#!/usr/bin/env python3

class Grid():
    def __init__(self):
        self.visited = False
        self.last_move = [0,0] # (x,y) address of the parent grid in the DFS route
        
        self.color = 6
        self.unvisited_neighbors = 4

        self.wall = [False,False,False,False]
        # 0_up, 1_right, 2_down, 3_left walls