"""
Pressure Widget Module according the the pressure points layout of the Sensomative mat
"""

from python_qt_binding import QtGui, QtCore
from python_qt_binding import QtWidgets

class pressureWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order = { # dictionary of positions with indexes as keys
            0: (1,1),
            1: (3,3),
            2: (5,1),
            3: (7,3),
            4: (10,1),
            5: (10,3),
            6: (10,6),
            7: (10,8),
            8: (7,6),
            9: (5,8),
            10: (3,6),
            11: (1,8),
        }
        
    def setMatrix(self, values):
        self.values = values
        self.update()


    @staticmethod
    def pressure_to_color(pressure):
        scaled_pressure = pressure / 255.0  
        r = min(1.0, 2 * scaled_pressure)  
        g = 1.0 - r  
        return int(r * 255), int(g * 255), 0 

    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        padding = 10  # Define padding
        roundness = 10.0  # Define corner roundness

        w = (self.geometry().width() - 2 * padding) / 8.
        h = (self.geometry().height() - 2 * padding) / 10.

        for index in self.order:
            temp = self.values[index]
            i, j = self.order[index]  # Swapping the i and j here for the rotation
            i -= 1 
            j -= 1
            r,g,b = self.pressure_to_color(temp)
            painter.setBrush(QtGui.QBrush(QtGui.QColor( r, g, b )))
            painter.drawRoundedRect(int(padding + j * w), int(padding + i * h), int(w), int(h), 5, 5)

        # Add a border to the widget
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))  

        # Draw a border rectangle with rounded corners
        outer_rect = QtCore.QRect(0, 0, self.geometry().width(), self.geometry().height())
        painter.drawRoundedRect(outer_rect, roundness, roundness)  

        painter.end()


        

