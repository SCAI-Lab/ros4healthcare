# This Python file uses the following encoding: utf-8
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap

from IconWidget import IconWidget
from pressureWidget import pressureWidget
from ecgWidget import ecgWidget


class RHDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        w = self.load_ui()
        layout = w.ADLLayout
        self.setObjectName("background")
        self.setStyleSheet("#background {background: qradialgradient( cx:0.5 cy:0.5, radius:0.8 fx:0.5, fy:0.5, stop:0 #0e79a5, stop:1 black);} * {color: white;}")
        mlayout = w.layout()
        exercise_icon = IconWidget(self)
        exercise_icon.loadIcon("exercise.png")
        exercise_icon.setTime("4h")
        exercise_icon.setType("Exercise")
        exercise_icon.setAngle(100)
        layout.addWidget(exercise_icon)
        leisure_icon = IconWidget(self)
        leisure_icon.loadIcon("leisure.png")
        leisure_icon.setTime("6h")
        leisure_icon.setType("Leisure")
        leisure_icon.setAngle(60)
        layout.addWidget(leisure_icon)
        social_icon = IconWidget(self)
        social_icon.loadIcon("social.png")
        social_icon.setTime("1h")
        social_icon.setType("Social")
        social_icon.setAngle(30)
        layout.addWidget(social_icon)
        mobility_icon = IconWidget(self)
        mobility_icon.loadIcon("mobility.png")
        mobility_icon.setTime("2h")
        mobility_icon.setType("Mobility")
        mobility_icon.setAngle(10)
        layout.addWidget(mobility_icon)
        transfer_icon = IconWidget(self)
        transfer_icon.loadIcon("transfer.png")
        transfer_icon.setTime("0.5h")
        transfer_icon.setType("Transfer")
        transfer_icon.setAngle(150)
        layout.addWidget(transfer_icon)
        selfcare_icon = IconWidget(self)
        selfcare_icon.loadIcon("selfcare.png")
        selfcare_icon.setTime("0.5h")
        selfcare_icon.setType("Self care")
        selfcare_icon.setAngle(150)
        layout.addWidget(selfcare_icon)
        resting_icon = IconWidget(self)
        resting_icon.loadIcon("resting.png")
        resting_icon.setTime("0.5h")
        resting_icon.setType("Resting")
        resting_icon.setAngle(150)
        layout.addWidget(resting_icon)
        w.rrLabel.setText("40")
        w.hrLabel.setText("75")

        w.ADLIconLabel.setPixmap(QPixmap("social-icon.png"))
        w.ADLTitleLabel.setText("Social")
        
        eW = ecgWidget(self)
        w.rightLayout.addWidget(eW)

        # pW = pressureWidget(self)
        # pW.setMatrix((0,25,35,45,60,80,100,120,150,170,200,255))
        # w.rightLayout.addWidget(pW)

        # remove the old widget
        # w.ecgWidget.deleteLater()

        # create and add the new widget
        # self.ecg_widget = ecgWidget(self)
        # w.rightLayout.addWidget(self.ecg_widget)




        self.setLayout(mlayout)

    def load_ui(self):
        loader = QUiLoader()
        path = Path(__file__).resolve().parent / "form.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        w = loader.load(ui_file, self)
        ui_file.close()
        return w


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RHDashboard()
    widget.show()
    sys.exit(app.exec())
