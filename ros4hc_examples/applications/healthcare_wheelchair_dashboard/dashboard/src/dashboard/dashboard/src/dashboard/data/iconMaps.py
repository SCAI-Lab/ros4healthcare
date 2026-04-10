from PyQt5.QtGui import QPixmap
import os

def get_mpixmaps(package_path, pkg_name):
    return {
        'Exercise': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/exercise-icon.png")),
        'Leisure': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/leisure-icon.png")),
        'Social': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/social-icon.png")),
        'Mobility': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/mobility-icon.png")),
        'Transfer': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/transfer-icon.png")),
        'Selfcare': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/selfcare-icon.png")),
        'Resting': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/resting-icon.png")),
    }

def get_cus_mpixmaps_(package_path, pkg_name):
    return {
        'Resting': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/resting-icon.png")),
        'Self Propulsion': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/mobility-icon.png")),
        'Arm Raises': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/exercise-icon.png")),
        'Transfer': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/transfer-icon.png")),
        'Using Phone': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/leisure-icon.png")),
        'Conversation': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/social-icon.png")),
        'Washing Hands': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/selfcare-icon.png")),
        'Eating,Drinking': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/leisure-icon.png")),
        'Assisted Propulsion': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/mobility-icon.png")),
        'Working on Computer': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/social-icon.png")),
        'Changing Clothes': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/selfcare-icon.png")),
        'Pressure Relief': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/transfer-icon.png")),
    }
    

def get_cus_mpixmaps():
    return {
        'Resting':  "resource/resting-icon.png",
        'Self Propulsion': "resource/mobility-icon.png",
        'Arm Raises': "resource/exercise-icon.png",
        'Transfer': "resource/transfer-icon.png",
        'Using Phone':  "resource/leisure-icon.png",
        'Conversation': "resource/social-icon.png",
        'Washing Hands': "resource/selfcare-icon.png",
        'Eating,Drinking': "resource/leisure-icon.png",
        'Assisted Propulsion': "resource/mobility-icon.png",
        'Working on Computer': "resource/social-icon.png",
        'Changing Clothes': "resource/selfcare-icon.png",
        'Pressure Relief': "resource/transfer-icon.png",
        'Empty': ''
    }

def get_main_adlpixmaps_(package_path, pkg_name):
    return {
        'Resting': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Resting.png")),
        'Self Propulsion': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Mobility.png")),
        'Arm Raises': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Exercise.png")),
        'Transfer': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Transfer.png")),
        'Using Phone': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Leisure.png")),
        'Conversation': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Social.png")),
        'Washing Hands': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Selfcare.png")),
        'Eating,Drinking': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Eating.png")),
        'Assisted Propulsion': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Mobility.png")),
        'Working on Computer': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Social.png")),
        'Changing Clothes': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Selfcare.png")),
        'Pressure Relief': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/State-Transfer.png")),
    }

def get_main_adlpixmaps(package_path, pkg_name):
    return {
        'Resting':  "resource/State-Resting.png",
        'Self Propulsion':  "resource/State-Mobility.png",
        'Arm Raises':  "resource/State-Exercise.png",
        'Transfer':  "resource/State-Transfer.png",
        'Using Phone':  "resource/State-Leisure.png",
        'Conversation':  "resource/State-Social.png",
        'Washing Hands':  "resource/State-Selfcare.png",
        'Eating,Drinking':  "resource/State-Eating.png",
        'Assisted Propulsion':  "resource/State-Mobility.png",
        'Working on Computer':  "resource/State-Social.png",
        'Changing Clothes':  "resource/State-Selfcare.png",
        'Pressure Relief':  "resource/State-Transfer.png",
        'Empty':  "resource/State-Empty.png",
    }

def get_sleep_adlpixmaps_(package_path, pkg_name):
    return {
        'Awake': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/SleepingState-Awake.png")),
        'Deep Sleep': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/SleepingState-Deep.png")),
        'Fair Sleep': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/SleepingState-Fair.png")),
        'Light Sleep': QPixmap(os.path.join(package_path, 'share', pkg_name, "resource/SleepingState-Light.png")),
    }

def get_sleep_state_adlpixmaps(package_path, pkg_name):
    return {
        'Awake': "resource/SleepingState-Awake.png",
        'Deep Sleep': "resource/SleepingState-Deep.png",
        'Fair Sleep': "resource/SleepingState-Fair.png",
        'Light Sleep': "resource/SleepingState-Light.png",
    }

def get_sleep_posture_names():
    return {
        0 : "Supine",
        1 : "Left",
        2 : "Prone",
        3 : "Right",
        4 : "Empty Bed",
        5 : "Moving",
    }
def get_sleep_posture_adlpixmaps():
    return {
        0 : "resource/Sleep_Pose_Supine.png",
        1 : "resource/Sleep_Pose_Left.png",
        2 : "resource/Sleep_Pose_Prone.png",
        3 : "resource/Sleep_Pose_Right.png",
        4 : "resource/Sleep_Pose_Empty.png",
        5 : "resource/Sleep_Pose_Moving.png",
    }