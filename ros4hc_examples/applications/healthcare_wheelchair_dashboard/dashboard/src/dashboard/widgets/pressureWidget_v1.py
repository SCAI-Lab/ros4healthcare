# This Python file uses the following encoding: utf-8
from python_qt_binding import QtGui
from python_qt_binding import QtWidgets

class pressureWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order=[
            0, 1, 10, 11,
            2, 3,  8,  9,
            4, 5,  6,  7,
        ]
    def setMatrix(self, values):
        self.values = values
        self.update()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        w = self.geometry().width()/5.
        h = self.geometry().height()/4.
        ew = w/5.
        eh = h/4.
        for j in range(3):
            for i in range(4):
                temp = self.values[self.order[j*4+i]]
                painter.setBrush(QtGui.QBrush(QtGui.QColor(min(255,2*(temp)),min(255,2*(255-temp)),0)))
                painter.drawRoundedRect(int((ew+i*(w+ew))), int(eh+j*(h+eh)), int(w), int(h), 5, 5)

        painter.end()
