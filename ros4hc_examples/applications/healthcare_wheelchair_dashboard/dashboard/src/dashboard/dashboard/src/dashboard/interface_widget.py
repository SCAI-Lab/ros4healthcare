"""
Main entry point for the ROSHealth Dashboard widgets on ROS
"""

import os
import time

from ament_index_python.resources import get_resource

from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout , QPushButton
from PyQt5.QtGui import QPixmap




from rclpy import logging

from std_msgs.msg import String
from ros_healthcare_msg.msg import HR, RR, ECGLeads 
from sensor_msgs.msg import Imu


from scipy.signal import butter, lfilter
import numpy as np


from dashboard_msg.msg import  Dashboard, SensorData
from ros_healthcare_msg.msg import Pressure, ADL
## wiget imports ##
import dashboard.widgets as widgets


## asset imports
from dashboard.data.iconMaps import get_mpixmaps, get_main_adlpixmaps, get_cus_mpixmaps
from dashboard.data.iconMaps import get_sleep_posture_names, get_sleep_posture_adlpixmaps

class InterfaceWidget(QWidget):

    def __init__(self, node, pkg_name='dashboard', ui_filename='form.ui'):
        super(InterfaceWidget, self).__init__()
        

        # logging.basicConfig(filename='/home/nishi/Schreibtisch/application.log', level=logging.INFO, format='%(asctime)s %(message)s')
        self._logger = logging.get_logger("InterfaceWidget")

        _, package_path = get_resource('packages', pkg_name)
        ui_file = os.path.join(package_path, 'share', pkg_name, 'resource', ui_filename)

        a = QWidget(self)
        loadUi(ui_file, a)
        self.a = a
    
        # LOGOs
        a.logoETH.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/logoETH.png")))
        a.logoSCAI.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/logoSCAI.png")))
        a.logoTOHOKU.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/logoTOHOKU.png")))
        # a.logoRH.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/RH_logo.png")))
        # a.logoRH.setScaledContents(True)

        # image maps for the adl classes
        self.mpixmaps = get_mpixmaps(package_path, pkg_name)
        self.cus_mpixmaps = get_cus_mpixmaps()
        self.main_adlpixmaps = get_main_adlpixmaps(package_path, pkg_name)
        
        # sleep poses assets
        self._sleep_poses_names = get_sleep_posture_names()
        self._sleep_poses_pixmaps = get_sleep_posture_adlpixmaps()

        layout = a.ADLLayout
        a.setStyleSheet("#RHDashboard {background: qradialgradient( cx:0.5 cy:0.5, radius:0.8 fx:0.5, fy:0.5, stop:0 #0e79a5, stop:1 black);} * {color: white;}")
        
        # Mid section icons
        self.exercise_icon = widgets.IconWidget.create_icon(a, "Exercise", "4h", 100, package_path, pkg_name, "exercise", layout)
        self.leisure_icon = widgets.IconWidget.create_icon(a, "Leisure", "6h", 60, package_path, pkg_name, "leisure", layout)
        self.social_icon = widgets.IconWidget.create_icon(a, "Social", "1h", 30, package_path, pkg_name, "social", layout)
        self.mobility_icon = widgets.IconWidget.create_icon(a, "Mobility", "2h", 10, package_path, pkg_name, "mobility", layout)
        self.transfer_icon = widgets.IconWidget.create_icon(a, "Transfer", "0.5h", 150, package_path, pkg_name, "transfer", layout)
        self.selfcare_icon = widgets.IconWidget.create_icon(a, "Self care", "0.5h", 150, package_path, pkg_name, "selfcare", layout)
        self.resting_icon = widgets.IconWidget.create_icon(a, "Resting", "0.5h", 150, package_path, pkg_name, "resting", layout)

        # buttons for activity widget : AWAKE / ASLEEP
        _activity_buttons_dict = {
            "AWAKE": lambda: self.switchWidget("AWAKE", self.a.activityLayout),
            "ASLEEP": lambda: self.switchWidget("ASLEEP", self.a.activityLayout)
        }
        _buttonsWidget = widgets.ButtonsWidget(_activity_buttons_dict)
        a.buttonLayoutActivity.addWidget(_buttonsWidget)
        
        ## Activity Widget

        # placeholder data for ADL, HR & RR
        self.activityWidgetAwake = widgets.activityWidget(self, package_path, pkg_name, "Empty","resource/social-icon.png", "resource/State-Empty.png", 400, 800)
        self.activityWidgetAsleep = widgets.activityWidget(self, package_path, pkg_name, "Empty","resource/social-icon.png.png", "resource/Sleep_Pose_Supine.png", 400, 800)
        self.activityWidgetAsleep.hide()
        # Add initial widget
        a.activityLayout.addWidget(self.activityWidgetAwake)

        ## HR & RR Widget
        a.label.setPixmap(QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/heart-signal.png")))
        a.rrLabel.setText("RR 40")
        a.hrLabel.setText("HR 75")

        ## HR history widget
        self.hrHistoryWidget = widgets.HRHistory(self)
        a.historyLayout.addWidget(self.hrHistoryWidget)

        # Add buttons to switch between biosignal widgets [ button_label : function ] 
        _biosignal_buttons_dict = {
            "ECG": lambda: self.switchWidget("ECG", self.a.biosignalLayout),
            "PPG": lambda: self.switchWidget("PPG", self.a.biosignalLayout),
            "IMU": lambda: self.switchWidget("IMU", self.a.biosignalLayout)
        }
        # _buttonsWidget = widgets.ButtonsWidget(_biosignal_buttons_dict)
        # a.buttonLayout.addWidget(_buttonsWidget)

        # initialise biosignal widgets
        self.ecgWidget = widgets.ecgWidget(self)
        self.ppgWidget = widgets.ppgWidget(self)
        self.imuWidget = widgets.ImuWidget(self)
        # self.imuWidget.hide()
        self.ppgWidget.hide()
        
        # Add initial widget
        a.biosignalLayout.addWidget(self.ecgWidget)
        a.imuLayout.addWidget(self.imuWidget)


        # Pressure Widget
        self.somnomatPressureWidget = widgets.pressureWidgetSleep(self)
        self.somnomatPressureWidget.setFixedSize(250,250) # set the widget size

        self.wheelchairPressureWidget = widgets.pressureWidget(self)
        self.wheelchairPressureWidget.setMatrix((0,25,35,45,60,80,100,120,150,170,200,255))
        self.wheelchairPressureWidget.setFixedSize(250,250) # set the widget size
        self.wheelchairPressureWidget.hide()

        # add buttons to switch between pressure widgets [ button_label : function ]
        _pressure_buttons_dict = {
            "WHEELCHAIR": lambda: self.switchWidget("WHEELCHAIR", self.a.pressureWidgetLayout),
            "SOMNOMAT": lambda: self.switchWidget("SOMNOMAT", self.a.pressureWidgetLayout),
        }

        _buttonsWidgetPW = widgets.ButtonsWidget(_pressure_buttons_dict)
        a.buttonLayoutPW.addWidget(_buttonsWidgetPW)
        
    
        # Add pWLayout to the right layout
        a.pressureWidgetLayout.addWidget(self.somnomatPressureWidget, 1)
        # a.pressureWidgetLayout.addWidget(self.wheelchairPressureWidget, 1)
        

        
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(a)

        time.sleep(1)

        # ROS2 Subscribers

        self.node = node
        self.sub_press = self.node.create_subscription(Pressure, "/pressure", self.press_callback, 10)
        self.sub_dash = self.node.create_subscription(Dashboard, "/dashboard", self.dash_callback, 1)
        self.sub_ecg = self.node.create_subscription(ECGLeads, "/ecg", self.ecg_callback, 10)
        self.sub_hr = self.node.create_subscription(HR, "/hr", self.hr_callback, 10)
        self.sub_rr = self.node.create_subscription(RR, "/rr", self.rr_callback, 10)
        self.sub_adl = self.node.create_subscription(String, "/adl_class", self.adl_callback, 10)
        self.sub_imu = self.node.create_subscription(Imu, "/imu", self.imu_callback, 10)

        # sensor mat
        self.sub_sensormat = self.node.create_subscription(SensorData, "/sensorMatress", self.sensormat_callback, 10)
        self.sub_sensormat_classifier = self.node.create_subscription(ADL, "/lyingPosition", self.sensormat_classifier_callback, 10)

    # Define function to switch widgets based on the selected button
    def switchWidget(self, buttonName, layout):
        # Delete current widgets
        _widget = layout.itemAt(0).widget()
        if _widget is not None:  # check if widget is None
            _widget.setParent(None)
        else:
            print(f"No widget at index to remove")


        # Add the new widget based on the pressed button
        if buttonName == "ECG":
            layout.addWidget(self.ecgWidget, 1)
        elif buttonName == "PPG":
            self.ppgWidget.show()
            layout.addWidget(self.ppgWidget, 1)
        elif buttonName == "IMU":
            self.imuWidget.show()
            layout.addWidget(self.imuWidget, 1)
        elif buttonName == "WHEELCHAIR":
            self.wheelchairPressureWidget.show()
            layout.addWidget(self.wheelchairPressureWidget, 1)
        elif buttonName == "SOMNOMAT":
            layout.addWidget(self.somnomatPressureWidget, 1)
        elif buttonName == "AWAKE":
            self.activityWidgetAwake.show()
            layout.addWidget(self.activityWidgetAwake, 1)
        elif buttonName == "ASLEEP":
            self.activityWidgetAsleep.show()
            layout.addWidget(self.activityWidgetAsleep, 1)
        else:
            self._logger.error(f"Button {buttonName} not found")

    def press_callback(self, msg):
        """
        Callback function for the wheelchair pressure mat topic.
        """
        self.wheelchairPressureWidget.setMatrix(msg.pressure)

    def sensormat_callback(self, msg):
        """
        Callback function for the sensormat pressure mat topic.
        """
        try: 
            image = msg.sensor_reading[0].pressure
            for entry in msg.sensor_reading[1:]:  # skip first entry because it is already in matrix
                newrow = entry.pressure
                image = np.vstack((image, newrow))  # stack lines of sensor data to get entire image
            
            # convert 2D array to dictionary
            if len(image) == 28 and len(image[0]) == 14:
                _update_data = {(i, j): image[i][j] for i in range(len(image)) for j in range(len(image[0]))}
                self.somnomatPressureWidget.setMatrix(_update_data)
            else:
                self._logger.error(f"Image size not correct. Received size: {np.shape(image)}")

        except Exception as e:
            self._logger.error(f"Error in callback: {e}")

    def dash_callback(self, msg):
        # setting the heart & respiration rate
        self.a.rrLabel.setText(str(msg.rr))
        self.a.hrLabel.setText(str(msg.hr))

        # setting the ADL time and angle
        self.exercise_icon.setTime(f"{msg.exe_hr} h")
        self.leisure_icon.setTime(f"{msg.lei_hr} h")
        self.social_icon.setTime(f"{msg.soc_hr} h")
        self.mobility_icon.setTime(f"{msg.mob_hr} h")
        self.transfer_icon.setTime(f"{msg.tra_hr} h")
        self.selfcare_icon.setTime(f"{msg.sel_hr} h")
        self.resting_icon.setTime(f"{msg.res_hr} h")
        
        self.exercise_icon.setAngle(min(msg.exe_per,1.0))
        self.leisure_icon.setAngle(min(msg.lei_per,1.0))
        self.social_icon.setAngle(min(msg.soc_per,1.0))
        self.mobility_icon.setAngle(min(msg.mob_per,1.0))
        self.transfer_icon.setAngle(min(msg.tra_per,1.0))
        self.selfcare_icon.setAngle(min(msg.sel_per,1.0))
        self.resting_icon.setAngle(min(msg.res_per,1.0))
        
        # setting the ADL icon and title
        self.a.ADLIconLabel.setPixmap(self.mpixmaps[msg.curadl.data])
        self.a.ADLTitleLabel.setText(msg.curadl.data)
    
    def adl_callback(self, msg):
        _title = msg.data
        _logo  = self.cus_mpixmaps[msg.data]
        _img   = self.main_adlpixmaps[msg.data]

        if _title == "Transfer" or _title == "Pressure Relief":
            _title = "Transfer"
        elif _title == "Assisted Propulsion":
            _title = "Assisted\nPropulsion"
        elif _title == "Eating,Drinking":
            _title = "Eating or\nDrinking"
        self.activityWidgetAwake.updateActivity(_title, _logo, _img)

        # [Debugging Log]
        self._logger.info(f"ADL : {_title}")
        # [Debugging Log]
        # logging.info(f"ADL : {_title}")


    def sensormat_classifier_callback(self, msg):
        _index = int(msg.prediction)
        _title = self._sleep_poses_names[_index]
        _img   = self._sleep_poses_pixmaps[_index]
        self.activityWidgetAsleep.updateActivity(title = _title, main_img_path=_img)

    def imu_callback(self, msg):
        self.imuWidget.update_imu_data(msg)

    def hr_callback(self, msg):
        self.a.hrLabel.setText("HR "+str(msg.hr[0]))

        # udpate the hr history
        self.hrHistoryWidget.update_hr_data(float(msg.hr[0]))

    def rr_callback(self, msg):
        self.a.rrLabel.setText("RR "+str(msg.rr[0]))
    
    def ecg_callback(self, msg):
        

        # # Apply low-pass filter
        # cutoff = 50.0  # desired cutoff frequency of the filter, Hz
        # fs = 128.0  # sample rate, Hz
        # filtered_ecg_data = butter_lowpass_filter(raw_ecg_data, cutoff, fs)

        # # Normalize the data to the range -1 to 1
        # normalized_ecg_data = 2 * (filtered_ecg_data - np.min(filtered_ecg_data)) / np.ptp(filtered_ecg_data) - 1

        try:
            raw_ecg_data = msg.leads[0].ecg
            self.ecgWidget.update_ecg_data(raw_ecg_data)
        except Exception as e:
            self._logger.error(f"Error in ECG callback: {e}")


# utility functions #

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

