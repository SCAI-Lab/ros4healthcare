import os
from glob import glob
from setuptools import setup, find_packages

package_name = 'polar_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=[package_name, f'{package_name}.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.py'))),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='spyros',
    maintainer_email='sgaryfallidi@student.ethz.ch',
    description='ROS2 wrapper to collect data from Polar H10',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
            'console_scripts': [
                    'polar_connector = polar_ros2.polar_ros2:main',
            ],
    },
)
