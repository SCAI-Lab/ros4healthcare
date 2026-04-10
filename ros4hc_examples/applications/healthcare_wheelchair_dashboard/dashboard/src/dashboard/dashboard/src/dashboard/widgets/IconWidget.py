# This Python file uses the following encoding: utf-8
from python_qt_binding import QtWidgets
from python_qt_binding import QtGui
from python_qt_binding import QtCore
from .ui_IconWidget import Ui_Form as Ui_IconWidget

import os


class IconWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(IconWidget, self).__init__(parent)

        self.m_ui = Ui_IconWidget()
        self.m_ui.setupUi(self)
        self.icon = None
        self.angle = 200
    def loadIcon(self, icon):
        self.icon = QtGui.QPixmap(icon)
    def setTime(self, time):
        self.m_ui.timeLabel.setText(time)
    def setType(self, type):
        self.m_ui.typeLabel.setText(type)
    def setAngle(self, angle):
        self.angle = angle*240.
        self.update()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        m_brush = QtGui.QBrush(QtGui.QColor("#436877"))
        white_pen = QtGui.QPen(m_brush, 5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        white_pen.setColor(QtCore.Qt.white)
        painter.drawPixmap(3, 3, self.icon)
        painter.setPen(white_pen)
        painter.drawArc(3, 3, 120, 120, 210*16, int(-16*self.angle))
        painter.drawArc(13, 13, 100, 100, 210*16,int(-16*self.angle))

    @classmethod
    def create_icon(cls, parent, icon_type, time, angle, package_path, pkg_name, resource, layout):
        icon_widget = cls(parent)
        icon_widget.loadIcon(os.path.join(package_path, 'share', pkg_name, f"resource/{resource}.png"))
        icon_widget.setTime(time)
        icon_widget.setType(icon_type)
        icon_widget.setAngle(angle)
        layout.addWidget(icon_widget)

        return icon_widget
        
