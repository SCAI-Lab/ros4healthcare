"""
    widget for the ppg plot
"""
import numpy as np
from PyQt5.QtCore import QLineF, QPointF, Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget

class ppgWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initializing the data array for the ECG plot
        self.data = np.zeros(128)

        # dot for the current position
        self.dot_position = 0

  
    def update_ppg_data(self, new_data):
        # Divide the 128 data points over the animation's frames per second
        # Assuming animation is at 60 frames per second
        fps = 30
        num_samples_per_frame = len(new_data) // fps

        for i in range(fps):
            chunk = new_data[i*num_samples_per_frame : (i+1)*num_samples_per_frame]
            
            # Making space for the new data and inserting it at the end
            self.data = np.roll(self.data, -len(chunk))
            self.data[-len(chunk):] = chunk

            # Updating the dot position
            self.dot_position = len(self.data) - 1

            # Updating the plot
            self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width, height = self.width(), self.height()
        xscale, yscale = width / len(self.data), height / 4

        for i in range(len(self.data) - 1):
            # Calculate the alpha value based on the age of the data point
            alpha = int(255 * (i / len(self.data)))

            # Create a pen with the calculated alpha value
            pen = QPen(QColor(255, 255, 255, alpha), 1)
            painter.setPen(pen)

            x1, y1 = i * xscale, (self.data[i] * yscale) + yscale
            x2, y2 = (i + 1) * xscale, (self.data[i + 1] * yscale) + yscale
            painter.drawLine(QLineF(x1, y1, x2, y2))

        # Draw the moving dot at the current dot position
        dot_x = self.dot_position * xscale
        dot_y = (self.data[self.dot_position] * yscale) + yscale
        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        painter.drawEllipse(QPointF(dot_x, dot_y), 2, 2)


        # Add a border to the widget
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(QColor(58, 36, 59), 2))  

        # Draw a border rectangle with rounded corners
        outer_rect = QRect(0, 0, self.geometry().width(), self.geometry().height()-150)
        painter.drawRoundedRect(outer_rect, 10, 10)  