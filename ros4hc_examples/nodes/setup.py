from setuptools import setup

package_name = 'nodes'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lucas',
    maintainer_email='kupper.lucas@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sub_adl = '+package_name+'.subscriber_adl:main',
            'sub_device = '+package_name+'.subscriber_device:main',
            'sub_ecg = '+package_name+'.subscriber_ecg:main',
            'sub_eda = '+package_name+'.subscriber_eda:main',
            'sub_eeg = '+package_name+'.subscriber_eeg:main',
            'sub_hr = '+package_name+'.subscriber_hr:main',
            'sub_imu = '+package_name+'.subscriber_imu:main',
            'sub_posture = '+package_name+'.subscriber_posture:main',
            'sub_ppg = '+package_name+'.subscriber_ppg:main',
            'sub_rr = '+package_name+'.subscriber_rr:main',
            'sub_sleepstage = '+package_name+'.subscriber_sleepstage:main',            
        ],
    },
)
