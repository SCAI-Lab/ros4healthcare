"""
    Widget to track heart rate over time
"""

import numpy as np
from PyQt5.QtCore import QLineF, QPointF, Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget

class HRHistory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initializing the data array for the HR plot
        self.data = np.zeros(300)  # data array for 10 min of data at 1Hz sampling rate

        # dot for the current position
        self.dot_position = 0
  
    def update_hr_data(self, new_data):
        # Making space for the new data and inserting it at the end
        self.data = np.roll(self.data, -1)
        self.data[-1] = new_data

        # Updating the dot position
        self.dot_position = len(self.data) - 1

        # Updating the plot
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width, height = self.width(), self.height()*0.8
        xscale = width / len(self.data) if len(self.data) != 0 else 1
        # yscale = height / (max(self.data) + 1e-10) if max(self.data) != 0 else 1
        # Padding: leave 10% of the widget height
        padding_height = 0.4 * height
        padded_height = height - padding_height

        yscale = padded_height / (max(self.data) + 1e-10) if max(self.data) != 0 else 1


        for i in range(len(self.data) - 1):
            # Calculate the alpha value based on the age of the data point
            alpha = int(255 * (i / len(self.data)))

            # Create a pen with the calculated alpha value
            pen = QPen(QColor(255, 255, 255, alpha), 2)
            painter.setPen(pen)

            x1, y1 = i * xscale, height - (self.data[i] * yscale)
            x2, y2 = (i + 1) * xscale, height - (self.data[i + 1] * yscale)
            painter.drawLine(QLineF(x1, y1, x2, y2))

        # Draw the moving dot at the current dot position
        dot_x = self.dot_position * xscale
        dot_y = height - (self.data[self.dot_position] * yscale)
        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        painter.drawEllipse(QPointF(dot_x, dot_y), 2, 2)

        # Add a border to the widget
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))  

        # Draw a border rectangle with rounded corners
        outer_rect = QRect(0, 0, self.geometry().width(), int(self.geometry().height()*0.8))
        painter.drawRoundedRect(outer_rect, 10, 10) 
