import numpy as np
from PyQt5.QtCore import QLineF, QPointF, Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget

class ecgWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initializing the data array for the ECG plot
        self.data = np.zeros(128)

        # dot for the current position
        self.dot_position = 0

  
    

    def update_ecg_data(self, new_data):
        # if empty, return
        if len(new_data) == 0:
            return

        # Normalize new_data
        data_min = np.min(new_data)
        data_range = np.max(new_data) - data_min
        if data_range != 0:  # avoid division by zero
            new_data = (new_data - data_min) / data_range

        fps = 60
        num_samples_per_frame = len(new_data) // fps

        for i in range(fps):
            chunk = new_data[i*num_samples_per_frame : (i+1)*num_samples_per_frame]
            self.data = np.roll(self.data, -len(chunk))
            self.data[-len(chunk):] = chunk
            self.dot_position = len(self.data) - 1
            self.update()



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width, height = self.width(), self.height() + 20
        xscale = width / len(self.data)
        epsilon = 1e-10  # small constant to avoid division by zero
        yscale = height / (3 * max(abs(self.data)) + epsilon)

        for i in range(len(self.data) - 1):
            alpha = int(255 * (i / len(self.data)))
            pen = QPen(QColor(255, 255, 255, alpha), 2)
            painter.setPen(pen)

            x1, y1 = i * xscale, (height / 2) - (self.data[i] * yscale)
            x2, y2 = (i + 1) * xscale, (height / 2) - (self.data[i + 1] * yscale)
            painter.drawLine(QLineF(x1, y1, x2, y2))

        dot_x = self.dot_position * xscale
        dot_y = (height / 2) - (self.data[self.dot_position] * yscale) 
        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        painter.drawEllipse(QPointF(dot_x, dot_y), 2, 2)

        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))

        outer_rect = QRect(0, 0, self.geometry().width(), self.geometry().height()-20)
        painter.drawRoundedRect(outer_rect, 10, 10)

    """ old implementation 
    
    
    def update_ecg_data(self, new_data):
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

    def paintEvent_(self, event):
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
        painter.setPen(QPen(QColor(255, 255, 255), 2))  

        # Draw a border rectangle with rounded corners
        outer_rect = QRect(0, 0, self.geometry().width(), self.geometry().height()-50)
        painter.drawRoundedRect(outer_rect, 10, 10)  
    """