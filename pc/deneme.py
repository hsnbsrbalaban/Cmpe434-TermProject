from tkinter import Tk, Canvas

class Grid():
    def __init__(self):
        self.walls = [False, False, False, False]
        self.color = 6
        self.coordinate = [0, 0]

    def setCoordinate(self, x, y):
        self.coordinate[0] = x
        self.coordinate[1] = y


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

    x = grid.coordinate[0] * 50
    y = grid.coordinate[1] * 50
    
    x+=2
    y+=2
    print("X: " + str(x) + " Y: " + str(y))
    # c.create_line(x, y, x+50, y, width=widths[0]) #up
    # c.create_line(x+50, y, x+50, y+50, width=widths[1]) #right
    # c.create_line(x, y+50, x+50, y+50, width=widths[2]) #down
    # c.create_line(x, y, x, y+50, width=widths[3]) #left

    # up wall
    c.create_line(x, 454-y-50, x+50, 454-y-50, width=widths[0])
    # right wall
    c.create_line(x+50, 454-y, x+50, 454-y-50, width=widths[1])
    # down wall
    c.create_line(x, 454-y, x+50, 454-y, width=widths[2])
    # left wall
    c.create_line(x, 454-y, x, 454-y-50, width= widths[3])

root = Tk()
root.geometry('456x456')
c = Canvas(root, height=454, width=454)

grid = Grid()
grid.setCoordinate(4,4)
grid.walls = [True, True, True, True]

rectangle(c, grid)


c.pack()
root.mainloop()