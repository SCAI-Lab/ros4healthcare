# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_RHDashboard(object):
    def setupUi(self, RHDashboard):
        if not RHDashboard.objectName():
            RHDashboard.setObjectName(u"RHDashboard")
        RHDashboard.resize(1920, 1080)
        RHDashboard.setStyleSheet(u"#RHDashboard {\n"
"	background: qradialgradient( cx:0.5 cy:0.5, radius:0.8 fx:0.5, fy:0.5, stop:0 #0e79a5, stop:1 black);\n"
"}\n"
"\n"
"* {\n"
"	color: white;\n"
"}")
        self.horizontalLayout = QHBoxLayout(RHDashboard)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.groupBox = QGroupBox(RHDashboard)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setStyleSheet(u"QGroupBox {\n"
"	border: 3px solid white;\n"
"	border-radius: 20px;\n"
"	margin: 20px;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ADLIconLabel = QLabel(self.groupBox)
        self.ADLIconLabel.setObjectName(u"ADLIconLabel")
        self.ADLIconLabel.setMinimumSize(QSize(120, 120))

        self.horizontalLayout_2.addWidget(self.ADLIconLabel)

        self.ADLTitleLabel = QLabel(self.groupBox)
        self.ADLTitleLabel.setObjectName(u"ADLTitleLabel")
        font = QFont()
        font.setPointSize(40)
        font.setBold(True)
        self.ADLTitleLabel.setFont(font)

        self.horizontalLayout_2.addWidget(self.ADLTitleLabel)

        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.WheelchairImage = QLabel(self.groupBox)
        self.WheelchairImage.setObjectName(u"WheelchairImage")
        self.WheelchairImage.setPixmap(QPixmap(u"side-graphics.png"))

        self.verticalLayout.addWidget(self.WheelchairImage)

        self.verticalLayout.setStretch(1, 1)

        self.horizontalLayout.addWidget(self.groupBox)

        self.ADLLayout = QVBoxLayout()
        self.ADLLayout.setObjectName(u"ADLLayout")
        self.ADLLayout.setContentsMargins(20, -1, 80, -1)

        self.horizontalLayout.addLayout(self.ADLLayout)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setObjectName(u"rightLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(RHDashboard)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(100, 100))
        self.label.setPixmap(QPixmap(u"heart-signal.png"))
        self.label.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label)

        self.hrLabel = QLabel(RHDashboard)
        self.hrLabel.setObjectName(u"hrLabel")
        font1 = QFont()
        font1.setPointSize(30)
        font1.setBold(True)
        self.hrLabel.setFont(font1)
        self.hrLabel.setStyleSheet(u"* {\n"
"            font-size: 2em;\n"
"          }")
        self.hrLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.hrLabel)

        self.rrLabel = QLabel(RHDashboard)
        self.rrLabel.setObjectName(u"rrLabel")
        self.rrLabel.setFont(font1)
        self.rrLabel.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.rrLabel)

        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 1)

        self.rightLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout.addLayout(self.rightLayout)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(3, 4)
        self.horizontalLayout.setStretch(4, 1)

        self.retranslateUi(RHDashboard)

        QMetaObject.connectSlotsByName(RHDashboard)
    # setupUi

    def retranslateUi(self, RHDashboard):
        RHDashboard.setWindowTitle(QCoreApplication.translate("RHDashboard", u"RHDashboard", None))
        self.groupBox.setTitle("")
        self.ADLIconLabel.setText(QCoreApplication.translate("RHDashboard", u"Icon", None))
        self.ADLTitleLabel.setText(QCoreApplication.translate("RHDashboard", u"Title", None))
        self.WheelchairImage.setText("")
        self.label.setText("")
        self.hrLabel.setText(QCoreApplication.translate("RHDashboard", u"HeartRate", None))
        self.rrLabel.setText(QCoreApplication.translate("RHDashboard", u"RespiratoryRate", None))
    # retranslateUi

