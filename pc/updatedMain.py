import bluetooth, sys

from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLCDNumber, QSlider, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QGuiApplication, QColor, QBrush
from PyQt5.QtCore import Qt

class Grid():
    def __init__(self):
        self.visited = False

        self.walls = [False, False, False, False]
        self.coordinate = [0, 0]
        self.color = 6

        self.particles = [False, False, False, False]

    def setCoordinate(self, x, y):
        self.coordinate[0] = x
        self.coordinate[1] = y

class Map(QWidget):
    def __init__(self):
        super().__init__()

        self.mode = 0 # 0-mapping, 1-localization

        self.grids = [[Grid() for x in range(9)] for y in range(9)]
        for x in range(9):
            for y in range(9):
                self.grids[x][y].setCoordinate(x, y)

        self.initUI()
    
    def initUI(self):
        self.resize(456,456)
        self.center()

        self.setWindowTitle('Term Project')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        for i in range(9):
            for j in range(9):
                x = self.grids[i][j].coordinate[0] * 50 + 2
                y = self.grids[i][j].coordinate[1] * 50 + 2

                if self.grids[i][j].color == 0 or self.grids[i][j].color == 1:
                    qp.setPen(QPen(Qt.black, 0, Qt.DotLine))
                    qp.setBrush(QBrush(Qt.black, Qt.SolidPattern))
                    qp.drawRect(x, 454-y-50, 50, 50)
                elif self.grids[i][j].color == 2:
                    qp.setPen(QPen(Qt.blue, 0, Qt.DotLine))
                    qp.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
                    qp.drawRect(x, 454-y-50, 50, 50)
                elif self.grids[i][j].color == 3:
                    qp.setPen(QPen(Qt.green, 0, Qt.DotLine))
                    qp.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                    qp.drawRect(x, 454-y-50, 50, 50)

                self.drawRect(qp, self.grids[i][j])

                if self.mode == 1:
                    self.drawParticles(qp, self.grids[i][j])
        
        qp.end()

    def drawRect(self, qp, grid):
        solidPen = QPen(Qt.black, 2, Qt.SolidLine)
        dashedPen = QPen(Qt.black, 1, Qt.DotLine)

        x = grid.coordinate[0] * 50 + 2
        y = grid.coordinate[1] * 50 + 2

        for i in range(4):
            if grid.walls[i]:
                qp.setPen(solidPen)
            else:
                qp.setPen(dashedPen)
            
            if i == 0: #up
                qp.drawLine(x, 454-y-50, x+50, 454-y-50)
            elif i == 1: #right
                qp.drawLine(x+50, 454-y, x+50, 454-y-50)
            elif i == 2: #down
                qp.drawLine(x, 454-y, x+50, 454-y)
            else: #left
                qp.drawLine(x, 454-y, x, 454-y-50)
    
    def drawParticles(self, qp, grid):
        print("")

    def updateGrid(self, grid):
        x = grid.coordinate[0]
        y = grid.coordinate[1]

        self.grids[x][y] = grid
        self.grids[x][y].visited = True
        
        self.update()
        QGuiApplication.processEvents()
    
    def updateParticles(self, heading, color, up, right, left):

    def spreadParticles():
        for i in range(9):
            for j in range(9):
                
                self.grids[i][j].particles = [True, True, True, True]
        

def decode_message_mapping(message):
    # m_xyurdlc
    x = int(message[2]) - 48 #48 is the ascii value of 0
    y = int(message[3]) - 48

    wall = [False, False, False, False]
    wall[0] = True if message[4] == ord("t") else False
    wall[1] = True if message[5] == ord("t") else False
    wall[2] = True if message[6] == ord("t") else False
    wall[3] = True if message[7] == ord("t") else False

    color = int(message[8]) - 48
    return x, y, color, wall

def decode_message_localization(message):
    # l_hcurl000
    heading = int(message[2]) - 48
    color = int(message[3]) - 48

    up = True if message[4] == ord("t") else False
    right = True if message[5] == ord("t") else False
    left = True if message[6] == ord("t") else False

if __name__ == '__main__':
    #Bluetooth init
    host_mac='02:16:53:47:F5:76' # robot's mac address
    port=4
    backlog=1
    size=9
    s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind(("", port))
    s.listen(backlog)
    #UI init
    app = QApplication(sys.argv)
    mapUI = Map()

    client, clientInfo = s.accept()
    while True:
        data = client.recv(size)
        if data:
            if data == "mapping_done":
                mapUI.spread_particles()
                mapUI.mode = 1
            elif data[0] == "m":
                x, y, color, wall = decode_message(data)
                grid = Grid()
                grid.setCoordinate(x,y)
                grid.walls = wall
                grid.color = color

                mapUI.updateGrid(grid)
            else:
                heading, color, up, right, left = decode_message_localization(data)
    