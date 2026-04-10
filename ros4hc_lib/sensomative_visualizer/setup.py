from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'sensomative_visualizer'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ricardo Manríquez / Hebba Hussein',
    maintainer_email='64954533+ricardo-manriquez@users.noreply.github.com',
    description='This is a visualizer for the pressure distribution of the sensomative pressure sensitive seat cushion, it subscribes to the pressure topic and publishes a stream of images that show the pressure distribution in a graphic way',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'visualizer = sensomative_visualizer.pressure_visualizer:main',
        ],
    },
)
