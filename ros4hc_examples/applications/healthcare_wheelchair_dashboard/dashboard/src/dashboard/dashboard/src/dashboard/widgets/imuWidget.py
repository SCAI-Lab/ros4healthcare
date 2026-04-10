import numpy as np
from PyQt5.QtCore import QLineF, QPointF, Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QWidget

class ImuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initializing the data arrays for the IMU plot
        self.data_x = np.zeros(128)
        self.data_y = np.zeros(128)
        self.data_z = np.zeros(128)

        # dot for the current position
        self.dot_position = 0

  
    def update_imu_data(self, new_data):
        # Normalize new_data for each axis
        self.data_x = self._update_axis_data(self.data_x, new_data.linear_acceleration.x)
        self.data_y = self._update_axis_data(self.data_y, new_data.linear_acceleration.y)
        self.data_z = self._update_axis_data(self.data_z, new_data.linear_acceleration.z)

        self.update()

    def _update_axis_data(self, data, new_value):
        data = np.roll(data, -1)
        data[-1] = new_value
        self.dot_position = len(data) - 1

        return data

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width, height = self.width(), self.height()
        xscale = width / len(self.data_x)

        # plot x data with red color
        self._draw_data(self.data_x, painter, xscale, QColor(255, 0, 0), 0, height / 3)

        # plot y data with green color
        self._draw_data(self.data_y, painter, xscale, QColor(0, 255, 0), height / 3, height / 3)

        # plot z data with blue color
        self._draw_data(self.data_z, painter, xscale, QColor(0, 0, 255), 2 * height / 3, height / 3)

        self._draw_legend(painter)

        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))

        outer_rect = QRect(0, 0, self.geometry().width(), self.geometry().height())
        painter.drawRoundedRect(outer_rect, 10, 10)

    def _draw_data(self, data, painter, xscale, color, yoffset, yheight):
        epsilon = 1e-10  # small constant to avoid division by zero
        yscale = yheight / (3 * max(abs(data)) + epsilon)

        for i in range(len(data) - 1):
            pen = QPen(color, 1)
            painter.setPen(pen)

            x1, y1 = i * xscale, yoffset + (yheight / 2) - (data[i] * yscale)
            x2, y2 = (i + 1) * xscale, yoffset + (yheight / 2) - (data[i + 1] * yscale)
            painter.drawLine(QLineF(x1, y1, x2, y2))

        dot_x = self.dot_position * xscale
        dot_y = yoffset + (yheight / 2) - (data[self.dot_position] * yscale)
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawEllipse(QPointF(dot_x, dot_y), 2, 2)

    def _draw_legend(self, painter):
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        legends = [('x', QColor(255, 0, 0)), ('y', QColor(0, 255, 0)), ('z', QColor(0, 0, 255))]

        for i, (text, color) in enumerate(legends):
            painter.setPen(QPen(color, 1))
            painter.setBrush(QBrush(color))
            painter.drawRect(self.width() - 50, 10 + i*20, 10, 10)

            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(self.width() - 35, 20 + i*20, text)

