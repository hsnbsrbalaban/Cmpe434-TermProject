import bluetooth
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from tkinter import Tk, Canvas



class Grid():
    def __init__(self):
        self.walls = [False, False, False, False]
        self.color = 6
        self.coordinate = [0, 0]

    def setCoordinate(self, x, y):
        self.coordinate[0] = x
        self.coordinate[1] = y

grids = [[Grid() for x in range(9)] for y in range(9)]
for x in range(9):
    for y in range(9):
        grids[x][y].setCoordinate(x, y)

def rectangle(c, grid):
    widths = [1, 1, 1, 1]
    if grid.walls[0]: #up
        widths[0] = 3
    if grid.walls[1]: #right
        widths[1] = 3
    if grid.walls[2]: #down
        widths[2] = 3
    if grid.walls[3]: #left
        widths[3] = 3

    x = grid.coordinate[0] * 50 + 2 # we add 2 for better visualization of the maze 
    y = grid.coordinate[1] * 50 + 2

    # up wall
    c.create_line(x, 454-y-50, x+50, 454-y-50, width=widths[0])
    # right wall
    c.create_line(x+50, 454-y, x+50, 454-y-50, width=widths[1])
    # down wall
    c.create_line(x, 454-y, x+50, 454-y, width=widths[2])
    # left wall
    c.create_line(x, 454-y, x, 454-y-50, width= widths[3])


def decode_message(message):
    # m_xyurdlc
    print(message)
    # x and y are positions
    x = int(message[2]) - 48 #48 is the ascii value of 0
    y = int(message[3]) - 48
    # u-up, r-right, d-down, l-left
    wall = [False, False, False, False]
    wall[0] = True if message[4] == ord("t") else False
    wall[1] = True if message[5] == ord("t") else False
    wall[2] = True if message[6] == ord("t") else False
    wall[3] = True if message[7] == ord("t") else False
    # c is color
    # color = int(message[8]) - 48
    color = 0
    print("X: " + str(x) + " Y: " + str(y))
    print("Up: " + str(wall[0]) + " Right: " + str(wall[1]) + " Down: " + str(wall[2]) + " Left: " + str(wall[3]))
    # print("Color: " + str(color) + "\n##########################################################################")
    return x, y, color, wall

host_mac='02:16:53:47:F5:76' # robot's mac address
port=4
backlog=1
size=8
s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind(("", port))
s.listen(backlog)

# try:
client, clientInfo = s.accept()
while True:
    data = client.recv(size)
    if data:
        x, y, color, wall = decode_message(data)
        grids[x][y].walls = wall

        root = Tk()
        root.geometry('456x456')
        c = Canvas(root, height=454, width=454)
        for i in range(9):
            for j in range(9):
                rectangle(c, grids[i][j])
        c.pack()
        root.mainloop()
            # client.send(data) # Echo back to client
# except:	
#     print("Closing socket")
#     client.close()
#     s.close()