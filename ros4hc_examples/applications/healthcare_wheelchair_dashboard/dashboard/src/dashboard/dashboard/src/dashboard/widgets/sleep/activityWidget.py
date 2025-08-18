"""
 Wiget for displaying the activity of the user
"""

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QRect

import os

class activityLogo(QLabel):
    def __init__(self, parent=None, package_path=None, pkg_name = None, img_path=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, img_path)))

class activityTitle(QLabel):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        font = QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.setFont(font)
        self.setText(title)

class activityMainImg(QLabel):
    def __init__(self, parent=None, package_path=None, pkg_name = None, img_path=None):
        super().__init__(parent)
        self.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, img_path)))


# define activity widget
class activityWidget(QWidget):

    # QVbox layout for the widget , with QHbox layout for the title and the logo and the main image
    def __init__(self, parent=None, package_path=None, pkg_name = None, titleText=None, logo_img_path=None, main_img_path=None, width=None, height=None):

        super().__init__(parent)

        self.package_path = package_path
        self.pkg_name = pkg_name

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        # create QHbox layout for the logo and the title
        self.title_logo_layout = QHBoxLayout()
        self.title_logo_layout.setAlignment(Qt.AlignCenter)
        self.title_logo_layout.setSpacing(0)
        self.title_logo_layout.setContentsMargins(0,0,0,0)

        # create title and logo
        self.title = activityTitle(self, title=titleText)
        self.logo = activityLogo(self, package_path=self.package_path, pkg_name=self.pkg_name, img_path=logo_img_path)
        
        self.title_logo_layout.addWidget(self.logo)
        self.title_logo_layout.addWidget(self.title)

        self.main_img = activityMainImg(self, package_path=self.package_path, pkg_name=self.pkg_name, img_path=main_img_path)
        self.main_img.setAlignment(Qt.AlignCenter)
        


        self.layout.addLayout(self.title_logo_layout)
        self.layout.addWidget(self.main_img)

        self.setLayout(self.layout)
        
        # fixed height
        self.setFixedHeight(900)

        if width is not None:  # if width is specified, set it
            self.setFixedWidth(width)

        if height is not None:  # if height is specified, set it
            self.setFixedHeight(height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Add a border to the widget
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(QPen(QColor(255, 255, 255), 2))  

        # Draw a border rectangle with rounded corners
        outer_rect = QRect(0, 0, self.geometry().width(), self.geometry().height())
        painter.drawRoundedRect(outer_rect, 10, 10)  

    # define the update function for the widget
    def updateActivity(self, title=None, logo_img_path=None, main_img_path=None):

        if title is not None:
            self.title.setText(title)

        if logo_img_path is not None:
            self.logo.setPixmap(QPixmap(os.path.join(self.package_path, 'share', self.pkg_name, logo_img_path)))

        if main_img_path is not None:
            _updateImg = QPixmap(os.path.join(self.package_path, 'share', self.pkg_name, main_img_path))
            _updateImg = _updateImg.scaled(QSize(600,600), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.main_img.setPixmap(QPixmap())
            self.main_img.setPixmap(_updateImg)



        self.update()