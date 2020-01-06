import sys, time
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QLCDNumber, QSlider, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QGuiApplication, QColor, QBrush
from PyQt5.QtCore import Qt

class Grid():
    def __init__(self):
        self.walls = [False, False, False, False]
        self.coordinate = [0, 0]
        self.color = 6

    def setCoordinate(self, x, y):
        self.coordinate[0] = x
        self.coordinate[1] = y

class Map(QWidget):
    def __init__(self):
        super().__init__()

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
                self.drawRect(qp, self.grids[i][j])
                if self.grids[i][j].color == 0 or self.grids[i][j].color == 1:
                    qp.setPen(QPen(Qt.green, 0, Qt.DotLine))
                    qp.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                    
                    x = self.grids[i][j].coordinate[0] * 50 + 2
                    y = self.grids[i][j].coordinate[1] * 50 + 2
                    qp.drawRect(x, 454-y-50, 50, 50)
        
        qp.end()
        

    def drawRect(self, qp, grid):
        solidPen = QPen(Qt.black, 3, Qt.SolidLine)
        dashedPen = QPen(Qt.black, 0, Qt.DotLine)

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


    def updateGrid(self, grid):
        x = grid.coordinate[0]
        y = grid.coordinate[1]

        self.grids[x][y] = grid
        
        self.update()
        QGuiApplication.processEvents()


if __name__ == '__main__' :
    app = QApplication(sys.argv)
    
    mapUI = Map()

    g = Grid()
    g.setCoordinate(4,4)
    g.walls = [True, True, True, True]
    g.color = 0

    t = Grid()
    t.setCoordinate(3,2)
    t.walls = [True, False, True, True]
    t.color = 0
    
    mapUI.updateGrid(g)
    mapUI.updateGrid(t)

    sys.exit(app.exec_())