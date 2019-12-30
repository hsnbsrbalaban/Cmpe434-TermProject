from tkinter import *

def rectangle(c, x, y, walls):
    widths = [1, 1, 1, 1]
    if walls[0]:
        widths[0] = 5
    if walls[1]:
        widths[1] = 5
    if walls[2]:
        widths[2] = 5
    if walls[3]:
        widths[3] = 5

    c.create_line(x, y, x+50, y, width=widths[0])
    c.create_line(x+50, y, x+50, y+50, width=widths[1])
    c.create_line(x, y+50, x+50, y+50, width=widths[0])
    c.create_line(x, y, x, y+50, width=widths[0])

root = Tk()
root.geometry('300x300')

c = Canvas(root, height=300, width=300)

rectangle(c, 50, 50, [True, False, True, False])

c.pack()

root.mainloop()