"""
Widget for adding buttons to the interface
"""

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup

# class ButtonsWidget(QWidget):
#     def __init__(self):
#         super().__init__()

#         # Create buttons with initial styles and make them checkable
#         self.ecgButton = QPushButton("ECG")
#         self.ecgButton.setCheckable(True)
#         self.ecgButton.setStyleSheet("QPushButton { background-color: black; color: white; } QPushButton:checked { background-color: darkblue; }")

#         self.ppgButton = QPushButton("PPG")
#         self.ppgButton.setCheckable(True)
#         self.ppgButton.setStyleSheet("QPushButton { background-color: black; color: white; } QPushButton:checked { background-color: darkblue; }")

#         self.imuButton = QPushButton("IMU")
#         self.imuButton.setCheckable(True)
#         self.imuButton.setStyleSheet("QPushButton { background-color: black; color: white; } QPushButton:checked { background-color: darkblue; }")

#         # Create button group to allow only one checked button at a time
#         self.buttonGroup = QButtonGroup()
#         self.buttonGroup.setExclusive(True)
#         self.buttonGroup.addButton(self.ecgButton)
#         self.buttonGroup.addButton(self.ppgButton)
#         self.buttonGroup.addButton(self.imuButton)

#         # Create a layout and add widgets
#         self.layout = QHBoxLayout(self)
#         self.layout.addWidget(self.ecgButton)
#         self.layout.addWidget(self.ppgButton)
#         self.layout.addWidget(self.imuButton)

#         self.setLayout(self.layout)

class ButtonsWidget(QWidget):
    def __init__(self, button_dict):
        super().__init__()

        # Create button group to allow only one checked button at a time
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)

        # Create a layout
        self.layout = QHBoxLayout(self)

        # Iterate over the dictionary and create buttons
        for button_label, button_lambda in button_dict.items():
            # Create button with initial styles and make it checkable
            button = QPushButton(button_label)
            button.setCheckable(True)
            button.setStyleSheet("QPushButton { background-color: black; color: white; } QPushButton:checked { background-color:  #0e79a5; }")
            
            # Connect the button's clicked signal to its corresponding lambda
            button.clicked.connect(button_lambda)

            # Add the button to the group and layout
            self.buttonGroup.addButton(button)
            self.layout.addWidget(button)

        self.setLayout(self.layout)

