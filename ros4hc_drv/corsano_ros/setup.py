from setuptools import setup, find_packages
from glob import glob
import os

package_name = 'corsano_ros'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='scai-lab',
    maintainer_email='moperez@ethz.ch',
    description='Corsano driver',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'corsano_ros = corsano_ros.corsano_ros_wrapper:main',
        ],
    },
)
