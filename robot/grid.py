#!/usr/bin/env python3

class Grid():
    def __init__(self):
        self.visited = False
        self.last_move = [0,0] # x, y
        
        self.color = 'white'
        self.non_visited_neighbors = 4

        self.left_wall = False
        self.right_wall = False
        self.up_wall = False
        self.down_wall = False