"""
Pressure Widget Module according the the pressure points layout of the Sensomative mat
"""

from PyQt5 import QtGui, QtCore, QtWidgets

class pressureWidgetSleep(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order = {  # dictionary of positions with indexes as keys
            (i, j): (i, j) for i in range(28) for j in range(14)
        }
        
        # initialize with dummy values
        self.values = {(i, j): min(255, 5 * (i + j)) for i in range(28) for j in range(14)}

    def setMatrix(self, updateValues=None):
        self.values = updateValues
        self.update()

    def calculate_dimensions(self):
        gap_y = 2  # Define gap size for vertical direction

        # Diameter of each circle considering the gap_y
        d = (self.geometry().height() - (27 * gap_y)) / 28.

        # Calculate the gap size for horizontal direction to fill the width
        gap_x = (self.geometry().width() - 14 * d) / 13.

        return d, gap_x, gap_y

    def calculate_padding(self, d, gap_x, gap_y):
        _offset = 10  # Define offset to the border of the widget

        # Total width and height of the grid including the gaps
        total_width = 14 * d + 13 * gap_x
        total_height = 28 * d + 27 * gap_y

        # Padding to center the grid within the widget
        padding_left = (self.geometry().width() - total_width) / 2 + _offset
        padding_top = (self.geometry().height() - total_height) / 2 + _offset

        return padding_left, padding_top
    
    @staticmethod
    def pressure_to_color(pressure):
        scaled_pressure = pressure / 5000.0
        r = min(1.0, scaled_pressure)  
        g = 1.0 - r  
        return int(r * 255), int(g * 255), 0 

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        d, gap_x, gap_y = self.calculate_dimensions()
        padding_left, padding_top = self.calculate_padding(d, gap_x, gap_y)

        for index in self.order:
            temp = self.values[index]
            i, j = self.order[index]  # Swapping the i and j here for the rotation
            i -= 1
            j -= 1

            # scale the temp
            # Use the pressure_to_color function for the color scaling
            r, g, b = self.pressure_to_color(temp)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(r, g, b)))

            # Draw a circle at the calculated position
            painter.drawEllipse(QtCore.QPointF(padding_left + j * (d + gap_x) + d / 2, padding_top + i * (d + gap_y) + d / 2), d / 2, d / 2)

        self.draw_border(painter)

        painter.end()

    def draw_border(self, painter):
        # Add a border to the widget
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))

        # Draw a border rectangle with rounded corners
        outer_rect = QtCore.QRect(0, 0, self.geometry().width(), self.geometry().height())
        painter.drawRoundedRect(outer_rect, 10, 10)
